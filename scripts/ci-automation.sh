#!/bin/bash
# ci-automation.sh — Complete CI/CD headless integration script
# Runs Claude Code for automated code review in a pipeline context.

set -euo pipefail

REPORT_FILE="claude-review-report.json"

echo "=== Claude Code CI Review ==="
echo "Branch: ${CI_BRANCH:-$(git branch --show-current)}"
echo "Commit: $(git rev-parse --short HEAD)"
echo ""

# Get the diff against the base branch
BASE_BRANCH="${CI_BASE_BRANCH:-main}"
DIFF=$(git diff "${BASE_BRANCH}"...HEAD 2>/dev/null || git diff HEAD~1)

if [ -z "$DIFF" ]; then
  echo "No changes to review."
  exit 0
fi

echo "Reviewing $(echo "$DIFF" | grep '^diff --git' | wc -l | tr -d ' ') changed files..."

# Run Claude Code with structured output
echo "$DIFF" | claude -p "
You are a code reviewer in a CI/CD pipeline. Review these changes and output JSON:
{
  "summary": "one-line summary of changes",
  "risk_level": "low|medium|high",
  "approval": true|false,
  "issues": [
    {"file": "path", "severity": "error|warning|info", "message": "description"}
  ],
  "suggestions": ["improvement suggestions"]
}
Be thorough but concise. Focus on bugs, security, and correctness.
" --output-format json --allowedTools "Read,Grep,Glob" --max-turns 15 > "$REPORT_FILE"

echo ""
echo "=== Review Complete ==="
echo "Report saved to: $REPORT_FILE"

# Parse results for CI pass/fail
if command -v jq &>/dev/null; then
  RISK=$(jq -r '.risk_level // "unknown"' "$REPORT_FILE" 2>/dev/null || echo "unknown")
  APPROVAL=$(jq -r '.approval // true' "$REPORT_FILE" 2>/dev/null || echo "true")
  ISSUES=$(jq '.issues | length' "$REPORT_FILE" 2>/dev/null || echo "0")

  echo "Risk Level: $RISK"
  echo "Issues Found: $ISSUES"
  echo "Approved: $APPROVAL"

  if [ "$APPROVAL" = "false" ]; then
    echo ""
    echo "⚠ Review flagged issues — check $REPORT_FILE for details"
    exit 1
  fi
fi

echo "✓ Review passed"
