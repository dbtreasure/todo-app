"""
Accept Edits Permission Mode

Demonstrates permission_mode="acceptEdits" — the agent can read AND
modify files without prompting, but dangerous operations like shell
commands still require approval (which blocks in a non-interactive
script, so we omit Bash from allowed_tools).

This is the right mode for automated refactoring, formatting, and
code modification tasks where you trust the agent to edit files.

Usage:
    uv run agent-sdk/python/accept_edits.py
"""

import asyncio
import sys

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    options = ClaudeAgentOptions(
        cwd="/tmp/work",
        permission_mode="acceptEdits",
        allowed_tools=["Read", "Glob", "Grep", "Edit", "Write"],
        model="claude-sonnet-4-5",
        max_turns=10,
    )

    prompt = (
        "Add JSDoc comments to every exported function in "
        "src/lib/actions.ts. Read the file first, then edit it."
    )

    print("Running agent with permission_mode='acceptEdits'...\n")

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)
        elif isinstance(message, ResultMessage):
            print(f"\n\nCost: ${message.total_cost_usd:.4f}")
            print(f"Duration: {message.duration_ms}ms")


if __name__ == "__main__":
    asyncio.run(main())
