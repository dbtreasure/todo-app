---
name: ArchitectReview
description: "Reviews code architecture and suggests improvements. Uses extended thinking."
argument-hint: "<directory-path>"
allowed-tools: [Bash, Read, Grep]
user-invocable: false
---

ultrathink

Given the codebase in the directory $ARGUMENTS[0]:
1. Identify architectural patterns
2. Find potential bottlenecks or design issues
3. Suggest refactoring with priority levels
4. Estimate impact of each suggestion

Focus on scalability and maintainability. Be specific with examples.
