"""
Streaming Output — Real-time Agent Responses

Demonstrates streaming agent output as it's generated,
handling different event types (text, tool_use, tool_result).

Usage:
    uv run agent-sdk/python/streaming_output.py
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

    print("Streaming agent response...\n")

    async for event in agent.run_streaming(
        "Analyze the project structure by reading package.json and "
        "the files in src/. Describe the architecture."
    ):
        if event.type == "text":
            print(event.text, end="", flush=True)
        elif event.type == "tool_use":
            print(f"\n[Tool: {event.tool_name}({event.tool_input})]")
        elif event.type == "tool_result":
            print(f"[Tool result: {len(str(event.output))} chars]")
        elif event.type == "done":
            print(f"\n\nDone. Tokens: {event.usage.input_tokens} in, {event.usage.output_tokens} out")


if __name__ == "__main__":
    asyncio.run(main())
