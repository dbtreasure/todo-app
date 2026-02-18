---
name: GenerateTestSuite
description: "Generates unit tests for a given source file."
argument-hint: "<source-file> [--coverage-target N]"
allowed-tools: [Write, Read, Bash]
user-invocable: true
model: sonnet
---

Generate a comprehensive test suite for $ARGUMENTS[0].

Target coverage: ${ARGUMENTS[1]:-85}%

Create tests that cover:
- Happy paths
- Edge cases
- Error conditions
- Integration points

Output: pytest-compatible Python file.
