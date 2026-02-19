"""
Streaming Output — Real-time Agent Responses

Demonstrates streaming agent output as it's generated using the
claude_agent_sdk query() async iterator. Messages arrive as
AssistantMessage (with TextBlock content) and ResultMessage (with
cost, duration, and session info) as the agent works.

Usage:
    uv run agent-sdk/python/streaming_output.py
"""

import asyncio
import sys
from pathlib import Path

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
    """Stream agent output in real time, printing text blocks as they arrive."""

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
        max_turns=5,
    )

    prompt = (
        "Analyze the project structure by reading package.json and "
        "the files in src/. Describe the architecture."
    )

    print("Streaming agent response...\n")

    async for message in query(prompt=prompt, options=options, cwd="/tmp/work"):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)
        elif isinstance(message, ResultMessage):
            print(f"\n\nDone.")
            print(f"Cost: ${message.total_cost_usd:.4f}")
            print(f"Duration: {message.duration_ms}ms")
            print(f"Session ID: {message.session_id}")


if __name__ == "__main__":
    asyncio.run(main())
