"""
Permission Callback — Delegate Mode

Demonstrates programmatic permission handling: the agent requests
permission for tools, and a callback function decides based on rules.

Usage:
    uv run agent-sdk/python/permission_callback.py
"""

import asyncio

from dotenv import load_dotenv

from claude_code_sdk import ClaudeCodeAgent, AgentConfig, PermissionRequest

load_dotenv()

# Define read-only tools that are always allowed
READONLY_TOOLS = {"Read", "Grep", "Glob"}

# Define tools that need explicit paths
WRITE_TOOLS = {"Edit", "Write"}
ALLOWED_WRITE_PATHS = {"src/", "tests/"}


def permission_handler(request: PermissionRequest) -> bool:
    """Decide whether to allow a tool call based on rules."""
    tool = request.tool_name

    # Always allow read-only tools
    if tool in READONLY_TOOLS:
        return True

    # Allow write tools only in permitted paths
    if tool in WRITE_TOOLS:
        file_path = request.tool_input.get("file_path", "")
        return any(file_path.startswith(prefix) for prefix in ALLOWED_WRITE_PATHS)

    # Block Bash by default in delegate mode
    if tool == "Bash":
        command = request.tool_input.get("command", "")
        # Allow safe commands
        safe_prefixes = ["npm test", "npm run lint", "npx tsc"]
        return any(command.startswith(prefix) for prefix in safe_prefixes)

    # Deny everything else
    return False


async def main():
    agent = ClaudeCodeAgent(
        config=AgentConfig(
            model="sonnet",
            permission_mode="delegate",
            max_turns=10,
        ),
        permission_callback=permission_handler,
    )

    result = await agent.run(
        "Read the todo-list component, identify any TypeScript type issues, "
        "and fix them."
    )

    print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
