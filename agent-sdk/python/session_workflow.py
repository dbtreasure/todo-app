"""
Session Workflow — Multi-Step Task Persistence

Demonstrates creating a session, doing work across multiple interactions,
and resuming the session later. The session_id is captured from the
ResultMessage of the first query() call, saved to a JSON file using
pathlib, and then passed via ClaudeAgentOptions(session_id=session_id)
in subsequent calls so the agent retains context between runs.

Usage:
    uv run agent-sdk/python/session_workflow.py

    Run multiple times to progress through phases 1 -> 2 -> 3.
"""

import asyncio
import json
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

SESSION_FILE = Path(__file__).parent / ".session_state.json"


def save_session(session_id: str, phase: int):
    """Persist session ID and progress phase to disk."""
    SESSION_FILE.write_text(
        json.dumps({"session_id": session_id, "phase": phase}, indent=2),
        encoding="utf-8",
    )


def load_session() -> dict | None:
    """Load saved session state from disk."""
    if SESSION_FILE.exists():
        return json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    return None


async def run_query(prompt: str, session_id: str | None = None) -> str | None:
    """Run a query, optionally resuming a session. Returns the session_id."""
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
        max_turns=5,
    )

    # If we have a previous session_id, resume it
    if session_id is not None:
        options = ClaudeAgentOptions(
            session_id=session_id,
            permission_mode="bypassPermissions",
            model="claude-sonnet-4-5",
            max_turns=5,
        )

    captured_session_id: str | None = None

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)
        elif isinstance(message, ResultMessage):
            captured_session_id = message.session_id
            print(f"\n\nCost: ${message.total_cost_usd:.4f}")
            print(f"Duration: {message.duration_ms}ms")

    return captured_session_id


async def main():
    saved = load_session()

    if saved:
        print(f"Resuming session {saved['session_id']} at phase {saved['phase']}...")
        session_id = saved["session_id"]
        phase = saved["phase"]
    else:
        print("Starting new session...")
        session_id = None
        phase = 1

    if phase == 1:
        print("\nPhase 1: Analyze the codebase...")
        new_session_id = await run_query(
            prompt=(
                "Analyze the project structure. Read package.json, the main "
                "page component, and the server actions. Summarize the architecture."
            ),
            session_id=session_id,
        )
        if new_session_id:
            save_session(new_session_id, phase=2)
            print(f"\nSession saved ({new_session_id}). Run again to continue to phase 2.")

    elif phase == 2:
        print("\nPhase 2: Deep dive into data layer...")
        new_session_id = await run_query(
            prompt=(
                "Now analyze the MongoDB connection and Mongoose model in detail. "
                "What are the schema fields? How is the connection managed?"
            ),
            session_id=session_id,
        )
        if new_session_id:
            save_session(new_session_id, phase=3)
            print(f"\nSession saved ({new_session_id}). Run again to continue to phase 3.")

    elif phase == 3:
        print("\nPhase 3: Generate recommendations...")
        await run_query(
            prompt=(
                "Based on your analysis in phases 1 and 2, provide a prioritized "
                "list of improvements for this codebase."
            ),
            session_id=session_id,
        )

        # Clean up session file after workflow is complete
        SESSION_FILE.unlink(missing_ok=True)
        print("\nWorkflow complete. Session cleaned up.")


if __name__ == "__main__":
    asyncio.run(main())
