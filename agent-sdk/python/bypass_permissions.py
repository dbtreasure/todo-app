"""
Bypass Permissions Mode

Demonstrates permission_mode="bypassPermissions" — the agent has
full unrestricted access to all tools including shell commands.
No prompts, no approvals.

This is for trusted automation pipelines, CI/CD, and environments
where you have full control and accept the risk. Never use this
with untrusted prompts.

Usage:
    uv run agent-sdk/python/bypass_permissions.py
"""

import asyncio
import sys

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    options = ClaudeAgentOptions(
        cwd="/tmp/work",
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
        max_turns=10,
    )

    prompt = (
        "Run 'npx tsc --noEmit' to check for TypeScript errors in the "
        "todo-app. If there are any errors, read the relevant files and "
        "fix them."
    )

    print("Running agent with permission_mode='bypassPermissions'...\n")

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)
        elif isinstance(message, ResultMessage):
            print(f"\n\nCost: ${message.total_cost_usd:.4f}")
            print(f"Duration: {message.duration_ms}ms")


if __name__ == "__main__":
    asyncio.run(main())
