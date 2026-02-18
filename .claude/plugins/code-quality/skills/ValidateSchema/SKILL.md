---
name: ValidateSchema
description: "Validates data files against JSON Schema definitions."
argument-hint: "<data-file> <schema-file>"
allowed-tools: [Read, Bash]
user-invocable: true
model: haiku
---

Validate $ARGUMENTS[0] against the schema in $ARGUMENTS[1].

Steps:
1. Read the data file
2. Read the schema file
3. Validate using JSON Schema rules
4. Report: valid/invalid with specific error locations

Return structured output with validation results.
