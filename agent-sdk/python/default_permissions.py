"""
Default Permission Mode

Demonstrates permission_mode="default" — the safest mode. The agent
is restricted to read-only tools so it can explore the codebase but
cannot modify anything.

This is the right mode for analysis, auditing, and code review tasks
where you want answers but no side effects.

Usage:
    uv run agent-sdk/python/default_permissions.py
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
        permission_mode="default",
        allowed_tools=["Read", "Glob", "Grep"],
        model="claude-sonnet-4-5",
        max_turns=10,
    )

    prompt = (
        "Review the todo-app source code. List every file, summarize "
        "what each one does, and flag any potential issues."
    )

    print("Running agent with permission_mode='default' (read-only tools)...\n")

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
