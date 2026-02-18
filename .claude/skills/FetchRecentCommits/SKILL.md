---
name: FetchRecentCommits
description: "Returns recent commits in the current repository."
argument-hint: "--max N"
allowed-tools: [Bash]
user-invocable: true
context: fork
agent: Explore
---

Latest 5 commits in this repo:
```
`git log --oneline -n 5`
```

Summarize their purpose and impact. Focus on what changed, not the details.
