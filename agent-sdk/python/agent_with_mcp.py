"""
Agent with MCP -- Playwright Browser Automation

Demonstrates configuring an external MCP server via dict config in
ClaudeAgentOptions and using query() to run a prompt with MCP tools.

No MCPConnection class -- just a plain dict in mcp_servers.

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
            "playwright": {
                "command": "npx",
                "args": ["@playwright/mcp@latest"],
            },
        },
        allowed_tools=[
            "mcp__playwright__browser_navigate",
            "mcp__playwright__browser_snapshot",
            "mcp__playwright__browser_click",
            "mcp__playwright__browser_type",
        ],
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
    )

    async for message in query(
        prompt=(
            "Navigate to https://news.ycombinator.com and take a snapshot. "
            "List the top 5 stories currently on the front page."
        ),
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"Session: {message.session_id}")


if __name__ == "__main__":
    asyncio.run(main())
