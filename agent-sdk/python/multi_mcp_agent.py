"""
Multi-MCP Agent -- Multiple Connections

Demonstrates an agent connected to multiple MCP servers simultaneously
via the mcp_servers dict config, combining tools from different services.

Usage:
    uv run agent-sdk/python/multi_mcp_agent.py
"""

import asyncio
import os
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
        cwd="/tmp/work",
        mcp_servers={
            "postgres": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-postgres",
                    os.environ.get(
                        "DATABASE_URL", "postgresql://localhost:5432/todoDb"
                    ),
                ],
            },
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": os.environ.get(
                        "GITHUB_TOKEN", ""
                    ),
                },
            },
        },
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
        max_turns=10,
    )

    async for message in query(
        prompt=(
            "Check the database for todos with 'bug' in the title, then search "
            "GitHub issues in the current repo for related open issues. "
            "Correlate the findings."
        ),
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"\nCost: ${message.total_cost_usd:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
