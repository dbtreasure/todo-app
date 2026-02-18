#!/bin/bash
# headless-examples.sh — Claude Code headless mode examples
# These are reference examples, not meant to be run all at once.

set -euo pipefail

# ── 1. Basic headless mode (skip all permission prompts) ──────────
# WARNING: Only use in trusted CI/CD environments
claude -p "Analyze the project structure and list all API endpoints" \
  --dangerously-skip-permissions

# ── 2. Tool whitelisting (safer alternative) ──────────────────────
# Only allow specific tools — no file writes, no bash
claude -p "Review src/lib/actions.ts for potential issues" \
  --allowedTools "Read,Grep,Glob"

# ── 3. JSON output format ─────────────────────────────────────────
# Get structured output for programmatic consumption
claude -p "List all TypeScript files with their line counts" \
  --output-format json

# ── 4. Budget caps with max turns ─────────────────────────────────
# Limit how many tool calls Claude can make
claude -p "Fix any lint errors in the project" \
  --max-turns 10 \
  --dangerously-skip-permissions

# ── 5. Piping input via stdin ─────────────────────────────────────
# Feed file content or command output directly
cat src/app/page.tsx | claude -p "Review this React component for performance issues" \
  --allowedTools "Read,Grep"

# ── 6. Using with git diff ────────────────────────────────────────
# Review only changed code
git diff HEAD~1 | claude -p "Review these changes for bugs or issues" \
  --output-format json

# ── 7. Combining flags ───────────────────────────────────────────
# Full CI/CD example: limited tools, JSON output, budget cap
claude -p "Analyze the codebase for security vulnerabilities" \
  --allowedTools "Read,Grep,Glob" \
  --output-format json \
  --max-turns 20
