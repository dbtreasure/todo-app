---
name: GenerateTests
description: "Generates unit tests for Python functions using pytest."
argument-hint: "<python-file>"
allowed-tools: [Read, Write, Bash]
user-invocable: true
model: sonnet
---

Generate comprehensive pytest tests for the functions in $ARGUMENTS[0].

Include:
- Unit tests for each function
- Edge case coverage
- Mock external dependencies
- Docstring-based test discovery

Output: test_*.py file in the same directory.
