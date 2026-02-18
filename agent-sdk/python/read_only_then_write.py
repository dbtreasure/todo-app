"""
Two-Phase Pattern: Read-Only Analysis -> Write-Capable Refactoring

Demonstrates the principle of least privilege:
1. First agent reads and analyzes code (read-only, can't break anything)
2. Second agent implements fixes based on the analysis (write access)

Usage:
    uv run agent-sdk/python/read_only_then_write.py
"""

import asyncio

from claude_code_sdk import ClaudeCodeAgent, AgentConfig


async def analyze_then_refactor(target_path: str) -> dict:
    """Run read-only analysis, then write-capable refactoring."""

    # Phase 1: Read-only analysis
    print(f"Phase 1: Analyzing {target_path}...")
    analyzer = ClaudeCodeAgent(
        config=AgentConfig(
            model="sonnet",
            permission_mode="read-only",
            max_turns=10,
            allowed_tools=["Read", "Grep", "Glob"],
        ),
        system_prompt=(
            "You are a code analyzer. Read and analyze the specified code. "
            "Identify specific issues: code smells, performance problems, "
            "type safety gaps, and improvement opportunities. "
            "Be precise with file paths and line numbers. "
            "You CANNOT modify any files — only read and report."
        ),
    )

    analysis_result = await analyzer.run(
        f"Analyze the code at {target_path} and list all issues found."
    )
    analysis = analysis_result.text
    print(f"  Analysis complete: found issues")

    # Phase 2: Write-capable refactoring
    print("Phase 2: Implementing fixes...")
    refactorer = ClaudeCodeAgent(
        config=AgentConfig(
            model="sonnet",
            permission_mode="workspace",
            max_turns=15,
            allowed_tools=["Read", "Edit", "Write", "Grep", "Glob"],
        ),
        system_prompt=(
            "You are a refactoring agent. Given an analysis of code issues, "
            "implement the recommended fixes. Make minimal, targeted changes. "
            "Do not refactor beyond what the analysis recommends."
        ),
    )

    refactor_result = await refactorer.run(
        f"Implement fixes for these issues:\n\n{analysis}"
    )

    return {
        "analysis": analysis,
        "refactoring": refactor_result.text,
    }


if __name__ == "__main__":
    result = asyncio.run(analyze_then_refactor("src/lib/actions.ts"))
    print("\n=== Complete ===")
    print(f"Analysis: {len(result['analysis'])} chars")
    print(f"Refactoring: {len(result['refactoring'])} chars")
