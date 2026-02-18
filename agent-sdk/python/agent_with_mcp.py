"""
Agent with MCP — Single Connection

Demonstrates connecting an agent to an MCP server, making the server's
tools available to the agent.

Usage:
    uv run agent-sdk/python/agent_with_mcp.py
"""

import asyncio

from dotenv import load_dotenv

from claude_code_sdk import ClaudeCodeAgent, AgentConfig, MCPConnection

load_dotenv()


async def main():
    # Connect to a PostgreSQL MCP server
    mcp = MCPConnection(
        name="postgres",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-postgres",
              "postgresql://localhost:5432/todoDb"],
    )

    agent = ClaudeCodeAgent(
        config=AgentConfig(
            model="sonnet",
            permission_mode="read-only",
            max_turns=10,
        ),
        mcp_connections=[mcp],
    )

    result = await agent.run(
        "Query the database to list all tables and their schemas. "
        "Then show me the 5 most recent todos."
    )

    print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
