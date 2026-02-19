"""
Agent with MCP -- Single Connection

Demonstrates connecting an agent to an MCP server via the mcp_servers
dict config in ClaudeAgentOptions. The dict replaces any MCPConnection
class -- just specify command, args, and optional env.

Usage:
    uv run agent-sdk/python/agent_with_mcp.py
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
        mcp_servers={
            "postgres": {
                "command": "npx",
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-postgres",
                    "postgresql://localhost:5432/todoDb",
                ],
            },
        },
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
        max_turns=10,
    )

    async for message in query(
        prompt=(
            "Query the database to list all tables and their schemas. "
            "Then show me the 5 most recent todos."
        ),
        options=options,
        cwd="/tmp/work",
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"\nCost: ${message.total_cost_usd:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
