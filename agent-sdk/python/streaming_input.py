"""
Streaming Input — Large File Chunked Processing

Demonstrates sending large inputs to the agent by reading and
chunking file contents, useful when processing large codebases
or log files.

Usage:
    uv run agent-sdk/python/streaming_input.py
"""

import asyncio
from pathlib import Path

from dotenv import load_dotenv

from claude_code_sdk import ClaudeCodeAgent, AgentConfig

load_dotenv()


async def analyze_large_input(file_paths: list[str]):
    """Read multiple files and send their combined content for analysis."""

    # Gather file contents
    chunks = []
    for path in file_paths:
        file_path = Path(path)
        if file_path.exists():
            content = file_path.read_text()
            chunks.append(f"--- {path} ---\n{content}")

    combined = "\n\n".join(chunks)
    print(f"Sending {len(combined)} chars from {len(chunks)} files for analysis...\n")

    agent = ClaudeCodeAgent(
        config=AgentConfig(
            model="sonnet",
            permission_mode="read-only",
            max_turns=5,
        ),
    )

    result = await agent.run(
        f"Analyze the following source files for code quality issues, "
        f"potential bugs, and improvement opportunities:\n\n{combined}"
    )

    print(result.text)
    print(f"\nTokens: {result.usage.input_tokens} in, {result.usage.output_tokens} out")


if __name__ == "__main__":
    files = [
        "src/app/page.tsx",
        "src/app/todo-list.tsx",
        "src/lib/actions.ts",
        "src/lib/mongodb.ts",
        "src/lib/models/todo.ts",
    ]
    asyncio.run(analyze_large_input(files))
