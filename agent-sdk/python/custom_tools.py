"""
Custom Tools -- Fibonacci Calculator

Demonstrates defining a custom tool with the @tool decorator,
registering it with create_sdk_mcp_server, and using ClaudeSDKClient
to process a prompt that invokes the tool.

Usage:
    uv run agent-sdk/python/custom_tools.py
"""

import asyncio
import sys

from dotenv import load_dotenv

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
    tool,
)

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@tool("calculate_fibonacci", "Calculate the Nth Fibonacci number (0-indexed, 0 to 50)", {"n": int})
def calculate_fibonacci(n: int) -> dict:
    """Calculate the nth Fibonacci number using iterative approach."""
    if n < 0 or n > 50:
        return {
            "content": [{"type": "text", "text": f"Error: n must be between 0 and 50, got {n}"}]
        }

    if n <= 1:
        result = n
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        result = b

    return {"content": [{"type": "text", "text": str(result)}]}


server = create_sdk_mcp_server(name="math", tools=[calculate_fibonacci])


async def main():
    options = ClaudeAgentOptions(
        mcp_servers={"math": server},
        allowed_tools=["mcp__math__calculate_fibonacci"],
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
    )

    client = ClaudeSDKClient(options)

    async for message in client.process(
        "Calculate the 10th, 20th, and 30th Fibonacci numbers. "
        "Then explain the growth rate of the Fibonacci sequence."
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"Session: {message.session_id}")


if __name__ == "__main__":
    asyncio.run(main())
