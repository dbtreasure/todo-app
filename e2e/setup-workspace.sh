#!/usr/bin/env bash
set -euo pipefail

BRANCH="${BRANCH:-17.1-agent-sdk-overview}"
WORK="/tmp/work"

if [ -d "$WORK/.git" ]; then
    echo "[setup] Workspace already exists at $WORK"
    echo "[setup] To re-clone, run: rm -rf $WORK && bash /setup-workspace.sh"
    cd "$WORK"
    echo "[setup] Current branch: $(git branch --show-current)"
    exit 0
fi

echo "[setup] Cloning branch '$BRANCH' into $WORK..."
cd /tmp
# Remove empty dir if it exists (created by Dockerfile for VS Code workspace)
[ -d "$WORK" ] && [ -z "$(ls -A "$WORK" 2>/dev/null)" ] && rm -rf "$WORK"

# The host repo (/repo) may only have the branch as a remote tracking ref
# (origin/BRANCH), not a local branch. Try direct clone first; if that fails,
# manually fetch the remote tracking ref.
if git clone --no-local --branch "$BRANCH" --single-branch /repo "$WORK" 2>/dev/null; then
    cd "$WORK"
else
    echo "[setup] Branch not found as local ref, trying remote tracking ref..."
    git init "$WORK"
    cd "$WORK"
    git remote add repo /repo
    git fetch repo "refs/remotes/origin/${BRANCH}:refs/heads/${BRANCH}"
    git checkout "$BRANCH"
fi

echo ""
echo "============================================"
echo "Workspace ready at $WORK"
echo "Branch: $(git branch --show-current)"
echo ""
echo "Agent SDK files:"
find agent-sdk -type f 2>/dev/null | sort || echo "  (none found)"
echo ""
echo "Quick start:"
echo "  cd $WORK"
echo "  cat agent-sdk/python/overview_example.py"
echo "  cat agent-sdk/typescript/overview-example.ts"
echo ""
echo "To run the Python example:"
echo "  uv venv /tmp/py-env"
echo "  source /tmp/py-env/bin/activate"
echo "  uv pip install claude-agent-sdk"
echo "  python3 agent-sdk/python/overview_example.py"
echo ""
echo "To run the TypeScript example:"
echo "  mkdir -p /tmp/ts-env && cd /tmp/ts-env"
echo "  npm init -y && npm install @anthropic-ai/claude-agent-sdk tsx"
echo "  NODE_PATH=/tmp/ts-env/node_modules npx tsx $WORK/agent-sdk/typescript/overview-example.ts"
echo ""
echo "To use Claude CLI directly:"
echo "  claude"
echo "============================================"
