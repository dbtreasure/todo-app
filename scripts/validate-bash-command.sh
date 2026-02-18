#!/bin/bash
# PreToolUse hook: block dangerous bash commands.
# Exit 0 = allow, Exit 2 = block.

INPUT="$1"
COMMAND=$(echo "$INPUT" | grep -o '"command":"[^"]*"' | sed 's/"command":"//;s/"$//' || echo "$INPUT")

DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf /*"
    "kill -9 -1"
    "DROP TABLE"
    "DROP DATABASE"
    "chmod -R 777 /"
    "curl .* | sh"
    "wget .* | bash"
)

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if echo "$COMMAND" | grep -qi "$pattern"; then
        echo "BLOCKED: $pattern" >&2
        exit 2
    fi
done

exit 0
