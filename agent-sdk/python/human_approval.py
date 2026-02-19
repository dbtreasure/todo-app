"""
Human-in-the-Loop Approval

Prompts the user in the terminal to approve or deny each tool call.
Uses a PreToolUse hook with input() for interactive approval.
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
    HookMatcher,
    ResultMessage,
    TextBlock,
    query,
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def human_approval_hook(input_data, tool_use_id, context):
    """Ask the human operator to approve each tool call."""
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

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
            return {}
        if response in ("n", "no"):
            return {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": "deny",
                    "permissionDecisionReason": (
                        f"Human operator denied {tool_name}"
                    ),
                }
            }
        print("Please enter 'y' or 'n'.")


async def main():
    options = ClaudeAgentOptions(
        cwd="/tmp/work",
        permission_mode="default",
        model="claude-sonnet-4-5",
        max_turns=10,
        hooks={
            "PreToolUse": [
                HookMatcher(matcher=".*", hooks=[human_approval_hook])
            ]
        },
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
