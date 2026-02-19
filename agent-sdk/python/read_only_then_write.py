"""
Two-Phase Pattern: Read-Only Analysis -> Write-Capable Refactoring

Demonstrates the principle of least privilege:
1. First agent reads and analyzes code (read-only, can't break anything)
2. Second agent implements fixes based on the analysis (write access)

Usage:
    uv run agent-sdk/python/read_only_then_write.py
"""

import sys
import asyncio

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def _collect_text(prompt: str, options: ClaudeAgentOptions) -> str:
    """Run a query and collect all text blocks into a single string."""
    parts: list[str] = []
    async for message in query(prompt=prompt, options=options, cwd="/tmp/work"):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    parts.append(block.text)
        elif isinstance(message, ResultMessage):
            print(f"  Cost: ${message.total_cost_usd:.4f} | Duration: {message.duration_ms}ms")
    return "\n".join(parts)


async def analyze_then_refactor(target_path: str) -> dict:
    """Run read-only analysis, then write-capable refactoring."""

    # Phase 1: Read-only analysis
    print(f"Phase 1: Analyzing {target_path}...")
    analyzer_options = ClaudeAgentOptions(
        allowed_tools=["Read", "Grep", "Glob"],
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
    )
    analysis_prompt = (
        "You are a code analyzer. Read and analyze the specified code. "
        "Identify specific issues: code smells, performance problems, "
        "type safety gaps, and improvement opportunities. "
        "Be precise with file paths and line numbers. "
        "You CANNOT modify any files -- only read and report.\n\n"
        f"Analyze the code at {target_path} and list all issues found."
    )
    analysis = await _collect_text(analysis_prompt, analyzer_options)
    print(f"  Analysis complete: found issues ({len(analysis)} chars)")

    # Phase 2: Write-capable refactoring (passes analysis as context)
    print("Phase 2: Implementing fixes...")
    refactorer_options = ClaudeAgentOptions(
        allowed_tools=["Read", "Edit", "Write", "Grep", "Glob"],
        permission_mode="acceptEdits",
        model="claude-sonnet-4-5",
    )
    refactor_prompt = (
        "You are a refactoring agent. Given an analysis of code issues, "
        "implement the recommended fixes. Make minimal, targeted changes. "
        "Do not refactor beyond what the analysis recommends.\n\n"
        f"Implement fixes for these issues:\n\n{analysis}"
    )
    refactoring = await _collect_text(refactor_prompt, refactorer_options)

    return {
        "analysis": analysis,
        "refactoring": refactoring,
    }


if __name__ == "__main__":
    result = asyncio.run(analyze_then_refactor("src/lib/actions.ts"))
    print("\n=== Complete ===")
    print(f"Analysis: {len(result['analysis'])} chars")
    print(f"Refactoring: {len(result['refactoring'])} chars")
