"""
Human-in-the-Loop Approval

Prompts the user in the terminal to approve or deny each tool call.
Uses the can_use_tool callback with input() for interactive approval.
Useful for supervised agent operation where a human reviews every action.

Usage:
    uv run agent-sdk/python/human_approval.py
"""

import asyncio
import json
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


async def human_permission_handler(
    tool_name: str, tool_input: dict, context: dict
) -> PermissionResultAllow | PermissionResultDeny:
    """Ask the human operator to approve each tool call."""

    separator = "=" * 60
    print(f"\n{separator}")
    print(f"Tool: {tool_name}")
    # Truncate large inputs to keep the display manageable
    input_preview = json.dumps(tool_input, indent=2)[:500]
    print(f"Input: {input_preview}")
    print(separator)

    while True:
        response = input("Allow this tool call? (y/n): ").strip().lower()
        if response in ("y", "yes"):
            return PermissionResultAllow(updated_input=tool_input)
        if response in ("n", "no"):
            return PermissionResultDeny(
                message=f"Human operator denied {tool_name}"
            )
        print("Please enter 'y' or 'n'.")


async def main():
    options = ClaudeAgentOptions(
        can_use_tool=human_permission_handler,
        permission_mode="default",
        model="claude-sonnet-4-5",
        max_turns=10,
    )

    prompt = (
        "Add a 'priority' field (low/medium/high) to the todo schema "
        "and update the server actions to support it."
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
