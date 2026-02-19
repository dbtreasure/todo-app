"""
Session Management — Capture, Store, List, Resume, and Fork Sessions

Demonstrates the session lifecycle using the real claude_agent_sdk API:
1. Run an initial query and capture session_id from ResultMessage
2. Store session info in a JSON file using pathlib
3. List saved sessions from the JSON store
4. Resume a session with ClaudeAgentOptions(resume=session_id)
5. Fork a session with fork_session=True for branching workflows

No fictional SessionManager class — all session tracking is done via
a simple JSON file managed with pathlib.

Usage:
    uv run agent-sdk/python/manage_sessions.py
"""

import asyncio
import json
import sys
from datetime import datetime, timezone
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

SESSIONS_FILE = Path(__file__).parent / ".sessions.json"


def load_sessions() -> list[dict]:
    """Load all saved sessions from the JSON store."""
    if SESSIONS_FILE.exists():
        return json.loads(SESSIONS_FILE.read_text(encoding="utf-8"))
    return []


def save_sessions(sessions: list[dict]):
    """Write sessions list to the JSON store."""
    SESSIONS_FILE.write_text(
        json.dumps(sessions, indent=2),
        encoding="utf-8",
    )


def add_session(session_id: str, description: str, cost_usd: float, duration_ms: int):
    """Add a new session entry to the store."""
    sessions = load_sessions()
    sessions.append({
        "session_id": session_id,
        "description": description,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "cost_usd": cost_usd,
        "duration_ms": duration_ms,
    })
    save_sessions(sessions)


def list_saved_sessions():
    """Print all saved sessions."""
    sessions = load_sessions()
    if not sessions:
        print("  No saved sessions found.")
        return
    for entry in sessions:
        print(
            f"  {entry['session_id']} | "
            f"created: {entry['created_at']} | "
            f"desc: {entry['description'][:60]}"
        )


async def run_and_capture(prompt: str, options: ClaudeAgentOptions) -> dict | None:
    """Run a query, print output, and return result metadata."""
    result_info: dict | None = None

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)
        elif isinstance(message, ResultMessage):
            result_info = {
                "session_id": message.session_id,
                "cost_usd": message.cost_usd,
                "duration_ms": message.duration_ms,
            }
            print(f"\n  Session ID: {message.session_id}")
            print(f"  Cost: ${message.cost_usd:.4f}")
            print(f"  Duration: {message.duration_ms}ms")

    return result_info


async def main():
    # Step 1: List any previously saved sessions
    print("=== Saved Sessions ===")
    list_saved_sessions()

    # Step 2: Create a new session with an initial query
    print("\n=== Creating New Session ===")
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
        max_turns=3,
    )

    result = await run_and_capture(
        prompt="What files are in the src/ directory? Give a brief overview.",
        options=options,
    )

    if not result:
        print("No result received.")
        return

    session_id = result["session_id"]
    add_session(
        session_id=session_id,
        description="Initial project overview",
        cost_usd=result["cost_usd"],
        duration_ms=result["duration_ms"],
    )
    print(f"\n  Session saved to {SESSIONS_FILE}")

    # Step 3: Resume the session to ask a follow-up question
    print("\n=== Resuming Session ===")
    resume_options = ClaudeAgentOptions(
        resume=session_id,
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
        max_turns=3,
    )

    resume_result = await run_and_capture(
        prompt="Based on what you just saw, which file is the main entry point?",
        options=resume_options,
    )

    if resume_result:
        add_session(
            session_id=resume_result["session_id"],
            description="Follow-up: identify main entry point",
            cost_usd=resume_result["cost_usd"],
            duration_ms=resume_result["duration_ms"],
        )

    # Step 4: Fork the session to explore a different direction
    print("\n=== Forking Session ===")
    fork_options = ClaudeAgentOptions(
        resume=session_id,
        fork_session=True,
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
        max_turns=3,
    )

    fork_result = await run_and_capture(
        prompt=(
            "Instead of the entry point, tell me about the data models "
            "and database layer from what you saw."
        ),
        options=fork_options,
    )

    if fork_result:
        add_session(
            session_id=fork_result["session_id"],
            description="Forked: explore data models",
            cost_usd=fork_result["cost_usd"],
            duration_ms=fork_result["duration_ms"],
        )

    # Step 5: Show all sessions after the workflow
    print("\n=== All Sessions After Workflow ===")
    list_saved_sessions()


if __name__ == "__main__":
    asyncio.run(main())
