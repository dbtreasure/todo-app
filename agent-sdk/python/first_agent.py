"""
First Agent -- Basic Claude Agent SDK Usage

Creates a query with options, iterates over streamed messages,
and prints the result.

Usage:
    uv run agent-sdk/python/first_agent.py
"""

import asyncio
import sys

from dotenv import load_dotenv

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
        max_turns=5,
    )

    async for message in query(
        prompt=(
            "Read src/lib/actions.ts and explain what each server action does, "
            "including its parameters and return type."
        ),
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"\nCost: ${message.total_cost_usd:.4f}")
            print(f"Duration: {message.duration_ms}ms")


if __name__ == "__main__":
    asyncio.run(main())
