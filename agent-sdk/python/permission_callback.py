"""
Permission Callback — Programmatic Tool Approval

Demonstrates programmatic permission handling using the can_use_tool
callback in ClaudeAgentOptions. The handler receives tool_name,
tool_input, and context, and returns PermissionResultAllow or
PermissionResultDeny.

Rules implemented:
- Always allow read-only tools (Read, Grep, Glob)
- Allow Edit/Write only for paths under src/ or tests/
- Allow Bash only for safe commands (npm test, npm run lint, npx tsc)
- Deny everything else

Usage:
    uv run agent-sdk/python/permission_callback.py
"""

import asyncio
import sys

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    PermissionResultAllow,
    PermissionResultDeny,
    ResultMessage,
    TextBlock,
    query,
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Read-only tools that are always allowed
READONLY_TOOLS = {"Read", "Grep", "Glob"}

# Write tools restricted to specific path prefixes
WRITE_TOOLS = {"Edit", "Write"}
ALLOWED_WRITE_PATHS = ("src/", "tests/")

# Bash commands allowed by prefix
SAFE_BASH_PREFIXES = ("npm test", "npm run lint", "npx tsc")


async def permission_handler(
    tool_name: str, tool_input: dict, context: dict
) -> PermissionResultAllow | PermissionResultDeny:
    """Decide whether to allow a tool call based on predefined rules."""

    # Always allow read-only tools
    if tool_name in READONLY_TOOLS:
        return PermissionResultAllow(updated_input=tool_input)

    # Allow write tools only in permitted paths
    if tool_name in WRITE_TOOLS:
        file_path = tool_input.get("file_path", "")
        if any(file_path.startswith(prefix) for prefix in ALLOWED_WRITE_PATHS):
            return PermissionResultAllow(updated_input=tool_input)
        return PermissionResultDeny(
            message=f"Write access denied: {file_path} is not in an allowed path"
        )

    # Allow Bash only for safe commands
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if any(command.startswith(prefix) for prefix in SAFE_BASH_PREFIXES):
            return PermissionResultAllow(updated_input=tool_input)
        return PermissionResultDeny(
            message=f"Bash command denied: '{command}' is not in the safe list"
        )

    # Deny everything else
    return PermissionResultDeny(message=f"Tool '{tool_name}' is not permitted")


async def main():
    options = ClaudeAgentOptions(
        cwd="/tmp/work",
        can_use_tool=permission_handler,
        permission_mode="default",
        model="claude-sonnet-4-5",
        max_turns=10,
    )

    prompt = (
        "Read the todo-list component, identify any TypeScript type issues, "
        "and fix them."
    )

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)
        elif isinstance(message, ResultMessage):
            print(f"\n\nDone. Cost: ${message.total_cost_usd:.4f}")
            print(f"Duration: {message.duration_ms}ms")


if __name__ == "__main__":
    asyncio.run(main())
