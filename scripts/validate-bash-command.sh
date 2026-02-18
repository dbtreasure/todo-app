#!/bin/bash
# validate-bash-command.sh
# PreToolUse hook for Bash — blocks dangerous command patterns.
# Exit 2 = block the tool call, Exit 0 = allow

# The tool input is passed via stdin as JSON
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | grep -o '"command":"[^"]*"' | head -1 | sed 's/"command":"//;s/"$//')

BLOCKED_PATTERNS=(
  "rm -rf /"
  "rm -rf /*"
  "kill -9"
  "dd if=/dev/zero"
  "> /etc/"
  "chmod 777"
  "DROP TABLE"
  "DROP DATABASE"
  ":(){ :|:& };:"
  "mkfs."
  "> /dev/sda"
)

for pattern in "${BLOCKED_PATTERNS[@]}"; do
  if [[ "$COMMAND" == *"$pattern"* ]]; then
    echo "{\"error\": \"Blocked dangerous command pattern: $pattern\"}" >&2
    exit 2
  fi
done

exit 0
