#!/bin/bash
# PreToolUse hook: validates bash commands before execution
# Blocks dangerous patterns that could cause harm

COMMAND="$1"

# Dangerous patterns to block
DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf /*"
    "kill -9"
    "mkfs"
    "dd if="
    "> /dev/sd"
    "chmod -R 777 /"
    ":(){ :|:& };:"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qF "$pattern"; then
        echo "BLOCKED: Command contains dangerous pattern: $pattern" >&2
        exit 2
    fi
done

exit 0
