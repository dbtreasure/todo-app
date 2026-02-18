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
- Happy paths with realistic data
- Edge cases and boundary conditions
- Error conditions and exception handling
- Integration points with other modules

Output: Create a test file adjacent to the source file using the project's test framework.
