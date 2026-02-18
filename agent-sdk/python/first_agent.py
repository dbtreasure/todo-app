"""
First Agent — Basic Claude Code SDK Usage

Creates an agent, sends a task, and prints the result.

Usage:
    uv run agent-sdk/python/first_agent.py
"""

import asyncio

from dotenv import load_dotenv

from claude_code_sdk import ClaudeCodeAgent, AgentConfig

load_dotenv()


async def main():
    agent = ClaudeCodeAgent(
        config=AgentConfig(
            model="sonnet",
            permission_mode="read-only",
            max_turns=5,
        ),
    )

    result = await agent.run(
        "Read src/lib/actions.ts and explain what each server action does, "
        "including its parameters and return type."
    )

    print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
