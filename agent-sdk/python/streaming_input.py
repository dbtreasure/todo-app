"""
Streaming Input — Large File Chunked Processing

Demonstrates sending large inputs to the agent by reading multiple
files with pathlib and constructing a detailed prompt from their
contents. The response is processed as a stream via the query()
async iterator.

Usage:
    uv run agent-sdk/python/streaming_input.py
"""

import asyncio
import sys
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def analyze_large_input(file_paths: list[str]):
    """Read multiple files and send their combined content for analysis.

    Gathers file contents using pathlib, constructs a single prompt
    with all source code, and streams the agent's analysis response.
    """

    # Gather file contents using pathlib for cross-platform compatibility
    chunks = []
    for path_str in file_paths:
        file_path = Path(path_str)
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            chunks.append(f"--- {file_path} ---\n{content}")
        else:
            print(f"Skipping (not found): {file_path}")

    if not chunks:
        print("No files found to analyze.")
        return

    combined = "\n\n".join(chunks)
    print(f"Sending {len(combined)} chars from {len(chunks)} files for analysis...\n")

    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
        max_turns=5,
    )

    prompt = (
        f"Analyze the following source files for code quality issues, "
        f"potential bugs, and improvement opportunities:\n\n{combined}"
    )

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)
        elif isinstance(message, ResultMessage):
            print(f"\n\nAnalysis complete.")
            print(f"Cost: ${message.cost_usd:.4f}")
            print(f"Duration: {message.duration_ms}ms")
            print(f"Session ID: {message.session_id}")


if __name__ == "__main__":
    # Example file paths — adjust to match your project structure
    files = [
        "src/app/page.tsx",
        "src/app/todo-list.tsx",
        "src/lib/actions.ts",
        "src/lib/mongodb.ts",
        "src/lib/models/todo.ts",
    ]
    asyncio.run(analyze_large_input(files))
