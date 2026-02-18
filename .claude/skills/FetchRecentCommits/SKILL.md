---
name: FetchRecentCommits
description: "Returns recent commits in the current repository with context."
argument-hint: "[--max N]"
allowed-tools: [Bash]
user-invocable: true
context: fork
agent: Explore
---

Latest commits in this repo:
```
`git log --oneline -n 10`
```

Current branch: `git branch --show-current`

Summarize the recent commit activity. Focus on what changed and any patterns
(e.g., feature work, bug fixes, refactoring). Be concise.
