"""
Custom Tools -- Fibonacci Calculator

Demonstrates defining a custom tool as a standalone MCP server using
the mcp library, registering it via mcp_servers in ClaudeAgentOptions,
and using query() to process a prompt that invokes the tool.

The MCP server is defined in this same file using FastMCP. When the SDK
launches it as a subprocess, FastMCP handles the stdio transport.

Usage:
    cd /tmp/work
    uv venv /tmp/py-env && source /tmp/py-env/bin/activate
    uv pip install claude-agent-sdk mcp python-dotenv
    python3 agent-sdk/python/custom_tools.py
"""

import asyncio
import os
import sys

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

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


# ---------------------------------------------------------------------------
# 1. Build a standalone MCP server that exposes a calculate_fibonacci tool
# ---------------------------------------------------------------------------

mcp = FastMCP("math")


@mcp.tool(
    name="calculate_fibonacci",
    description="Calculate the Nth Fibonacci number (0-indexed, 0 to 50)",
)
def calculate_fibonacci(n: int) -> str:
    """Calculate the nth Fibonacci number using iterative approach."""
    if n < 0 or n > 50:
        return f"Error: n must be between 0 and 50, got {n}"

    if n <= 1:
        result = n
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
        result = b

    return str(result)


# ---------------------------------------------------------------------------
# 2. Use the SDK to run a prompt with the custom tool
# ---------------------------------------------------------------------------


async def main():
    # Point the SDK at this file as an MCP server subprocess.
    # FastMCP detects the `mcp` object when run via `python -m mcp.server.fastmcp run`.
    script_path = os.path.abspath(__file__)

    options = ClaudeAgentOptions(
        mcp_servers={
            "math": {
                "command": sys.executable,
                "args": ["-m", "mcp.server.fastmcp", "run", script_path],
            },
        },
        allowed_tools=["mcp__math__calculate_fibonacci"],
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
    )

    async for message in query(
        prompt=(
            "Calculate the 10th, 20th, and 30th Fibonacci numbers. "
            "Then explain the growth rate of the Fibonacci sequence."
        ),
        options=options,
        cwd="/tmp/work",
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"\nSession: {message.session_id}")


if __name__ == "__main__":
    asyncio.run(main())
