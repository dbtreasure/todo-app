"""
Multi-MCP Agent — Multiple Connections

Demonstrates an agent connected to multiple MCP servers simultaneously,
combining tools from different services.

Usage:
    uv run agent-sdk/python/multi_mcp_agent.py
"""

import asyncio
import os

from dotenv import load_dotenv

from claude_code_sdk import ClaudeCodeAgent, AgentConfig, MCPConnection

load_dotenv()


async def main():
    # Database connection
    db_mcp = MCPConnection(
        name="postgres",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-postgres",
              os.environ.get("DATABASE_URL", "postgresql://localhost:5432/todoDb")],
    )

    # GitHub connection
    github_mcp = MCPConnection(
        name="github",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": os.environ.get("GITHUB_TOKEN", "")},
    )

    agent = ClaudeCodeAgent(
        config=AgentConfig(
            model="sonnet",
            permission_mode="read-only",
            max_turns=10,
        ),
        mcp_connections=[db_mcp, github_mcp],
    )

    result = await agent.run(
        "Check the database for todos with 'bug' in the title, then search "
        "GitHub issues in the current repo for related open issues. "
        "Correlate the findings."
    )

    print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
