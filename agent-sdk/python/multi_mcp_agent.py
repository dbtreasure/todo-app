"""
Multi-MCP Agent -- Multiple Server Configurations

Demonstrates an agent connected to multiple MCP servers simultaneously:
one stdio-based server and one SSE-based server. Shows how to restrict
which MCP tools the agent can use via allowed_tools.

No MCPConnection class -- just plain dicts in mcp_servers.

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
    # Stdio-based MCP server (filesystem access)
    filesystem_server = {
        "command": "npx",
        "args": [
            "-y",
            "@modelcontextprotocol/server-filesystem",
            os.environ.get("MCP_FILESYSTEM_ROOT", "/tmp"),
        ],
    }

    # SSE-based MCP server (remote API)
    api_server = {
        "type": "sse",
        "url": os.environ.get("MCP_API_SERVER_URL", "http://localhost:3001/sse"),
        "headers": {
            "Authorization": f"Bearer {os.environ.get('MCP_API_TOKEN', '')}",
        },
    }

    options = ClaudeAgentOptions(
        mcp_servers={
            "filesystem": filesystem_server,
            "api_server": api_server,
        },
        allowed_tools=[
            "mcp__filesystem__read_file",
            "mcp__filesystem__list_directory",
            "mcp__api_server__get_data",
            "mcp__api_server__search",
        ],
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
    )

    async for message in query(
        prompt=(
            "List the files in the configured root directory, then read any "
            "README or configuration files you find. Summarize what you learn."
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
