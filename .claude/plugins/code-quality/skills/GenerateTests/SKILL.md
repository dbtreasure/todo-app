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
- Happy path tests with realistic data
- Edge cases (empty input, None, boundary values)
- Error handling tests (expected exceptions)
- Parametrized tests where appropriate

Follow the project's existing test patterns. Place the test file adjacent to the source.
