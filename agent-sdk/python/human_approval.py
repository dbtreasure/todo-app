"""
Human-in-the-Loop Approval

Prompts the user in the terminal to approve or deny each tool call.
Useful for supervised agent operation.

Usage:
    uv run agent-sdk/python/human_approval.py
"""

import asyncio
import json

from dotenv import load_dotenv

from claude_code_sdk import ClaudeCodeAgent, AgentConfig, PermissionRequest

load_dotenv()


def human_permission_handler(request: PermissionRequest) -> bool:
    """Ask the human operator to approve each tool call."""
    print(f"\n{'=' * 60}")
    print(f"Tool: {request.tool_name}")
    print(f"Input: {json.dumps(request.tool_input, indent=2)[:500]}")
    print(f"{'=' * 60}")

    while True:
        response = input("Allow? (y/n): ").strip().lower()
        if response in ("y", "yes"):
            return True
        if response in ("n", "no"):
            return False
        print("Please enter 'y' or 'n'.")


async def main():
    agent = ClaudeCodeAgent(
        config=AgentConfig(
            model="sonnet",
            permission_mode="delegate",
            max_turns=10,
        ),
        permission_callback=human_permission_handler,
    )

    result = await agent.run(
        "Add a 'priority' field (low/medium/high) to the todo schema "
        "and update the server actions to support it."
    )

    print("\n" + result.text)


if __name__ == "__main__":
    asyncio.run(main())
