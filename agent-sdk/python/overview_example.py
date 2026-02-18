"""
Minimal Claude Code Agent SDK Example (Python)

Demonstrates the simplest possible agent: create a session, send a message,
and print the response.

Usage:
    uv run agent-sdk/python/overview_example.py
"""

import asyncio

from claude_code_sdk import ClaudeCodeAgent, AgentConfig


async def main():
    agent = ClaudeCodeAgent(
        config=AgentConfig(
            model="sonnet",
            permission_mode="read-only",
            max_turns=3,
        ),
    )

    result = await agent.run(
        "List all TypeScript files in src/ and summarize the project structure."
    )

    print("Agent response:")
    print(result.text)
    print(f"\nTokens used: {result.usage.input_tokens} in, {result.usage.output_tokens} out")


if __name__ == "__main__":
    asyncio.run(main())
