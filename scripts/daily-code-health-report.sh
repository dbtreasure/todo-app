#!/bin/bash
# daily-code-health-report.sh — Automated daily code health report
# Runs lint, analyzes git history, and generates a markdown summary.

set -euo pipefail

REPORT_DATE=$(date +%Y-%m-%d)
REPORT_FILE="reports/code-health-${REPORT_DATE}.md"

mkdir -p reports

echo "Generating code health report for ${REPORT_DATE}..."

# Gather data
LINT_OUTPUT=$(npm run lint 2>&1 || true)
GIT_LOG=$(git log --oneline --since="1 day ago" 2>/dev/null || echo "No commits in last 24h")
GIT_STATS=$(git diff --stat HEAD~5 2>/dev/null || echo "No recent changes")
FILE_COUNT=$(find src -name "*.ts" -o -name "*.tsx" | wc -l | tr -d ' ')
TODO_COUNT=$(grep -r "TODO\|FIXME\|HACK" src/ 2>/dev/null | wc -l | tr -d ' ')

# Generate report via Claude
cat <<PROMPT_EOF | claude -p "$(cat)" --output-format text --allowedTools "Read,Grep,Glob" --max-turns 10 > "$REPORT_FILE"
Generate a markdown code health report for ${REPORT_DATE}.

Project: Todo App (Next.js 15 + MongoDB)
TypeScript files: ${FILE_COUNT}
TODO/FIXME count: ${TODO_COUNT}

Recent commits:
${GIT_LOG}

Recent file changes:
${GIT_STATS}

Lint output:
${LINT_OUTPUT}

Format as a professional daily report with sections:
# Code Health Report — ${REPORT_DATE}
## Summary (2-3 sentences)
## Recent Activity
## Code Quality
## Action Items (prioritized list)
## Metrics
PROMPT_EOF

echo "Report saved to: ${REPORT_FILE}"
