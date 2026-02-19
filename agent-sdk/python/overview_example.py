"""
Minimal Claude Agent SDK Example (Python)

Demonstrates the simplest possible usage: send a prompt using query(),
iterate over streamed messages, and print the response.

Usage:
    uv run agent-sdk/python/overview_example.py
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
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
        max_turns=3,
    )

    print("Agent response:")
    async for message in query(
        prompt="List all TypeScript files in src/ and summarize the project structure.",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"\nCost: ${message.total_cost_usd:.4f}")
            print(f"Duration: {message.duration_ms}ms")
            print(f"Session ID: {message.session_id}")


if __name__ == "__main__":
    asyncio.run(main())
