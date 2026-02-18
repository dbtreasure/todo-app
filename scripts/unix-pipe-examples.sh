#!/bin/bash
# unix-pipe-examples.sh — Using Claude Code as a Unix pipe utility
# These are reference examples demonstrating stdin/stdout patterns.

set -euo pipefail

# ── 1. Pipe git diff for review ──────────────────────────────────
git diff HEAD~1 | claude -p "Review this diff. List any bugs or concerns." \
  --allowedTools "Read,Grep"

# ── 2. Pipe file content for analysis ─────────────────────────────
cat src/lib/actions.ts | claude -p "
  Analyze this server actions file. Are there any:
  - Missing error handling?
  - N+1 query patterns?
  - Unvalidated inputs?
" --allowedTools "Read"

# ── 3. Process a list of files ────────────────────────────────────
find src -name "*.tsx" -type f | claude -p "
  These are all React component files. Which ones are likely candidates
  for code splitting or lazy loading? Output as JSON array of file paths.
" --output-format json --allowedTools "Read,Grep"

# ── 4. Chain Claude calls ─────────────────────────────────────────
# First call identifies issues, second call suggests fixes
claude -p "List all TODO comments in the codebase" \
  --allowedTools "Grep" --output-format json | \
claude -p "Given this list of TODOs, prioritize them by importance
  and suggest an implementation order." --output-format json

# ── 5. JSON schema enforcement ────────────────────────────────────
git log --oneline -20 | claude -p "
  Categorize these commits. Output JSON matching this schema:
  {
    "features": ["commit descriptions"],
    "bugfixes": ["commit descriptions"],
    "refactoring": ["commit descriptions"],
    "other": ["commit descriptions"]
  }
" --output-format json

# ── 6. Generate documentation from code ───────────────────────────
cat src/lib/actions.ts | claude -p "
  Generate JSDoc comments for each exported function.
  Output only the documented version of the file.
" --allowedTools "Read"
