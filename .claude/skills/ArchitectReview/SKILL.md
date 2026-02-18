---
name: ArchitectReview
description: "Reviews code architecture and suggests improvements. Uses extended thinking for deep analysis."
argument-hint: "<directory-path>"
allowed-tools: [Bash, Read, Grep]
user-invocable: false
---

ultrathink

Given the codebase in the directory $ARGUMENTS[0]:
1. Identify architectural patterns (MVC, layered, event-driven, etc.)
2. Find potential bottlenecks or design issues
3. Suggest refactoring with priority levels (P0-P3)
4. Estimate impact of each suggestion (low/medium/high effort)

Focus on scalability and maintainability. Be specific with file paths and examples.
