#!/usr/bin/env bash
set -euo pipefail

BRANCH="${BRANCH:-17.1-agent-sdk-overview}"
TIER="${TIER:-T1}"

echo "============================================"
echo "E2E Test Runner"
echo "Branch: $BRANCH"
echo "Tier:   $TIER"
echo "============================================"

# -------------------------------------------------------------------
# 1. Clone the repo from the read-only mount into a writable workspace
# -------------------------------------------------------------------
WORK="/tmp/work"
echo ""
echo "[setup] Cloning branch '$BRANCH' into $WORK..."
git clone --no-local --branch "$BRANCH" --single-branch /repo "$WORK"
cd "$WORK"

# -------------------------------------------------------------------
# 2. Discover files to test
# -------------------------------------------------------------------
PY_FILES=()
TS_FILES=()

if [ -d "agent-sdk/python" ]; then
    while IFS= read -r f; do
        PY_FILES+=("$f")
    done < <(find agent-sdk/python -name '*.py' -type f 2>/dev/null)
fi

if [ -d "agent-sdk/typescript" ]; then
    while IFS= read -r f; do
        TS_FILES+=("$f")
    done < <(find agent-sdk/typescript -name '*.ts' -type f 2>/dev/null)
fi

echo "[setup] Found ${#PY_FILES[@]} Python files, ${#TS_FILES[@]} TypeScript files"

# -------------------------------------------------------------------
# 3. Verification: no old SDK references
# -------------------------------------------------------------------
echo ""
echo "[verify] Checking for stale SDK references..."
FAIL=0

if grep -r "claude_code_sdk" agent-sdk/ 2>/dev/null; then
    echo "FAIL: Found references to old 'claude_code_sdk' package"
    FAIL=1
fi

if grep -r "claude-code-sdk" agent-sdk/ 2>/dev/null | grep -v "# " | grep -v "^Binary"; then
    echo "FAIL: Found references to old 'claude-code-sdk' package name"
    FAIL=1
fi

# Check for wrong attribute names
if grep -rn 'message\.cost_usd[^_]' agent-sdk/ 2>/dev/null | grep -v 'total_cost_usd'; then
    echo "FAIL: Found 'cost_usd' (should be 'total_cost_usd')"
    FAIL=1
fi

if grep -rn 'costUsd\|durationMs\b\|sessionId\b' agent-sdk/ --include='*.ts' 2>/dev/null; then
    echo "FAIL: Found camelCase result fields in TypeScript (should be snake_case)"
    FAIL=1
fi

if [ "$FAIL" -eq 1 ]; then
    echo ""
    echo "VERIFICATION FAILED: stale references found"
    exit 1
fi
echo "[verify] No stale references found"

# -------------------------------------------------------------------
# T1: Parse — syntax validity without installing dependencies
# -------------------------------------------------------------------
run_t1() {
    echo ""
    echo "========== T1: Parse =========="
    local pass=0
    local fail=0

    for f in "${PY_FILES[@]}"; do
        if python3 -c "import ast; ast.parse(open('$f').read())" 2>/dev/null; then
            echo "  PASS (parse): $f"
            pass=$((pass + 1))
        else
            echo "  FAIL (parse): $f"
            fail=$((fail + 1))
        fi
    done

    # For TypeScript, verify files are non-empty valid UTF-8
    # Full type-checking (tsc --noEmit) happens in T2 after deps are installed
    for f in "${TS_FILES[@]}"; do
        if node -e "
            const fs = require('fs');
            const src = fs.readFileSync('$f', 'utf8');
            if (src.trim().length === 0) process.exit(1);
            // Basic structural checks: has imports and a function
            if (!src.includes('import') && !src.includes('require')) process.exit(1);
            process.exit(0);
        " 2>/dev/null; then
            echo "  PASS (parse): $f"
            pass=$((pass + 1))
        else
            echo "  FAIL (parse): $f"
            fail=$((fail + 1))
        fi
    done

    # Also check README for valid markdown (existence + no obvious issues)
    if [ -f "agent-sdk/README.md" ]; then
        echo "  PASS (exists): agent-sdk/README.md"
        pass=$((pass + 1))
    fi

    echo ""
    echo "T1 Results: $pass passed, $fail failed"
    [ "$fail" -eq 0 ] && return 0 || return 1
}

# -------------------------------------------------------------------
# T2: Import — install deps and verify imports resolve
# -------------------------------------------------------------------
run_t2() {
    echo ""
    echo "========== T2: Import =========="
    local pass=0
    local fail=0

    # Python setup
    if [ ${#PY_FILES[@]} -gt 0 ]; then
        echo "[T2] Setting up Python environment..."
        uv venv /tmp/py-env
        VIRTUAL_ENV=/tmp/py-env
        PATH="/tmp/py-env/bin:$PATH"
        uv pip install claude-agent-sdk 2>&1 | tail -1

        for f in "${PY_FILES[@]}"; do
            # Extract import lines and test them
            imports=$(python3 -c "
import ast, sys
tree = ast.parse(open('$f').read())
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and node.module:
        names = ', '.join(a.name for a in node.names)
        print(f'from {node.module} import {names}')
    elif isinstance(node, ast.Import):
        for a in node.names:
            print(f'import {a.name}')
" 2>/dev/null)

            if [ -n "$imports" ]; then
                if python3 -c "$imports" 2>/dev/null; then
                    echo "  PASS (import): $f"
                    pass=$((pass + 1))
                else
                    echo "  FAIL (import): $f"
                    python3 -c "$imports" 2>&1 | head -3
                    fail=$((fail + 1))
                fi
            else
                echo "  SKIP (no imports): $f"
            fi
        done
    fi

    # TypeScript setup
    if [ ${#TS_FILES[@]} -gt 0 ]; then
        echo "[T2] Setting up TypeScript environment..."
        mkdir -p /tmp/ts-env
        cd /tmp/ts-env
        npm init -y > /dev/null 2>&1
        npm install @anthropic-ai/claude-agent-sdk typescript @types/node 2>&1 | tail -1

        # Create tsconfig that skips type-checking node_modules (peer dep .d.ts)
        # but still validates our imports and usage
        cat > tsconfig.json << 'TSEOF'
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ES2022",
    "lib": ["ES2022"],
    "moduleResolution": "node",
    "esModuleInterop": true,
    "skipLibCheck": true,
    "noEmit": true,
    "strict": false
  },
  "include": ["test.ts"]
}
TSEOF
        cd "$WORK"

        for f in "${TS_FILES[@]}"; do
            # Copy file and try to compile with tsc
            cp "$f" /tmp/ts-env/test.ts
            if cd /tmp/ts-env && npx tsc -p tsconfig.json 2>/dev/null; then
                echo "  PASS (import): $f"
                pass=$((pass + 1))
            else
                echo "  FAIL (import): $f"
                npx tsc -p tsconfig.json 2>&1 | head -5
                fail=$((fail + 1))
            fi
            cd "$WORK"
        done
    fi

    echo ""
    echo "T2 Results: $pass passed, $fail failed"
    [ "$fail" -eq 0 ] && return 0 || return 1
}

# -------------------------------------------------------------------
# T3: Execute — actually run the scripts against the real API
# -------------------------------------------------------------------
run_t3() {
    echo ""
    echo "========== T3: Execute =========="

    if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
        echo "SKIP: ANTHROPIC_API_KEY not set, cannot run T3 tests"
        return 0
    fi

    local pass=0
    local fail=0

    # Ensure Python env exists (from T2 or create fresh)
    if [ ! -d /tmp/py-env ]; then
        uv venv /tmp/py-env
        VIRTUAL_ENV=/tmp/py-env
        PATH="/tmp/py-env/bin:$PATH"
        uv pip install claude-agent-sdk 2>&1 | tail -1
    fi

    for f in "${PY_FILES[@]}"; do
        echo "[T3] Running: python $f"
        if timeout 120 python3 "$f" 2>&1; then
            echo "  PASS (execute): $f"
            pass=$((pass + 1))
        else
            echo "  FAIL (execute): $f"
            fail=$((fail + 1))
        fi
    done

    # Ensure TS env exists
    if [ ! -d /tmp/ts-env/node_modules ]; then
        mkdir -p /tmp/ts-env
        cd /tmp/ts-env
        npm init -y > /dev/null 2>&1
        npm install @anthropic-ai/claude-agent-sdk typescript @types/node tsx 2>&1 | tail -1
        cd "$WORK"
    fi

    for f in "${TS_FILES[@]}"; do
        echo "[T3] Running: npx tsx $f"
        # Run from the ts-env to pick up node_modules
        if timeout 120 env NODE_PATH=/tmp/ts-env/node_modules npx --prefix /tmp/ts-env tsx "$WORK/$f" 2>&1; then
            echo "  PASS (execute): $f"
            pass=$((pass + 1))
        else
            echo "  FAIL (execute): $f"
            fail=$((fail + 1))
        fi
    done

    echo ""
    echo "T3 Results: $pass passed, $fail failed"
    [ "$fail" -eq 0 ] && return 0 || return 1
}

# -------------------------------------------------------------------
# Run requested tier(s)
# -------------------------------------------------------------------
TIER_UPPER=$(echo "$TIER" | tr '[:lower:]' '[:upper:]')

case "$TIER_UPPER" in
    T1)
        run_t1
        ;;
    T2)
        run_t1 && run_t2
        ;;
    T3)
        run_t1 && run_t2 && run_t3
        ;;
    ALL)
        run_t1 && run_t2 && run_t3
        ;;
    *)
        echo "Unknown tier: $TIER (expected T1, T2, T3, or ALL)"
        exit 1
        ;;
esac

echo ""
echo "============================================"
echo "All requested tests passed!"
echo "============================================"

# -------------------------------------------------------------------
# Format session logs into readable transcripts (after T3)
# -------------------------------------------------------------------
if [ "$TIER_UPPER" = "T3" ] || [ "$TIER_UPPER" = "ALL" ]; then
    LOG_DIR="$HOME/.claude/projects/-tmp-work"
    if [ -d "$LOG_DIR" ] && ls "$LOG_DIR"/*.jsonl >/dev/null 2>&1; then
        echo ""
        echo "========== Session Transcripts =========="
        for logfile in "$LOG_DIR"/*.jsonl; do
            python3 /format-log.py "$logfile"
            echo ""
        done
    fi
fi
