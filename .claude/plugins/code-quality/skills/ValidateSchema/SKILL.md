---
name: ValidateSchema
description: "Validates data files against JSON Schema or TypeScript types."
argument-hint: "<data-file> <schema-file>"
allowed-tools: [Read, Bash]
user-invocable: true
model: haiku
---

Validate the data file at $ARGUMENTS[0] against the schema at $ARGUMENTS[1].

Steps:
1. Read both files
2. Determine schema type (JSON Schema, TypeScript interface, Zod schema)
3. Validate the data against the schema
4. Report: valid/invalid, list of errors with paths, suggestions for fixes

Be concise and actionable.
