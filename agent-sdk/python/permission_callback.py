"""
Permission Callback — Programmatic Tool Approval

Demonstrates programmatic permission handling using PreToolUse hooks
in ClaudeAgentOptions. The hook receives input_data with tool_name
and tool_input, and returns a permission decision.

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
    HookMatcher,
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


async def permission_hook(input_data, tool_use_id, context):
    """Decide whether to allow a tool call based on predefined rules."""
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    # Always allow read-only tools
    if tool_name in READONLY_TOOLS:
        return {}

    # Allow write tools only in permitted paths
    if tool_name in WRITE_TOOLS:
        file_path = tool_input.get("file_path", "")
        if any(file_path.startswith(prefix) for prefix in ALLOWED_WRITE_PATHS):
            return {}
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"Write access denied: {file_path} is not in an allowed path"
                ),
            }
        }

    # Allow Bash only for safe commands
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        if any(command.startswith(prefix) for prefix in SAFE_BASH_PREFIXES):
            return {}
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"Bash command denied: '{command}' is not in the safe list"
                ),
            }
        }

    # Deny everything else
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": f"Tool '{tool_name}' is not permitted",
        }
    }


async def main():
    options = ClaudeAgentOptions(
        cwd="/tmp/work",
        permission_mode="default",
        model="claude-sonnet-4-5",
        max_turns=10,
        hooks={
            "PreToolUse": [
                HookMatcher(matcher=".*", hooks=[permission_hook])
            ]
        },
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
