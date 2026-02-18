"""
Session Workflow — Multi-Day Task Persistence

Demonstrates creating a session, doing work across multiple interactions,
and resuming the session later. The agent retains context between runs.

Usage:
    uv run agent-sdk/python/session_workflow.py
"""

import asyncio
import json
from pathlib import Path

from dotenv import load_dotenv

from claude_code_sdk import ClaudeCodeAgent, AgentConfig

load_dotenv()

SESSION_FILE = Path("agent-sdk/python/.session_state.json")


def save_session(session_id: str, phase: int):
    """Persist session ID and progress to disk."""
    SESSION_FILE.write_text(json.dumps({
        "session_id": session_id,
        "phase": phase,
    }))


def load_session() -> dict | None:
    """Load saved session state."""
    if SESSION_FILE.exists():
        return json.loads(SESSION_FILE.read_text())
    return None


async def main():
    saved = load_session()

    if saved:
        print(f"Resuming session {saved['session_id']} at phase {saved['phase']}...")
        agent = ClaudeCodeAgent(
            config=AgentConfig(
                model="sonnet",
                permission_mode="read-only",
                max_turns=5,
            ),
            session_id=saved["session_id"],
        )
        phase = saved["phase"]
    else:
        print("Starting new session...")
        agent = ClaudeCodeAgent(
            config=AgentConfig(
                model="sonnet",
                permission_mode="read-only",
                max_turns=5,
            ),
        )
        phase = 1

    if phase == 1:
        print("\nPhase 1: Analyze the codebase...")
        result = await agent.run(
            "Analyze the project structure. Read package.json, the main page component, "
            "and the server actions. Summarize the architecture."
        )
        print(result.text)
        save_session(agent.session_id, phase=2)
        print("\nSession saved. Run again to continue to phase 2.")

    elif phase == 2:
        print("\nPhase 2: Deep dive into data layer...")
        result = await agent.run(
            "Now analyze the MongoDB connection and Mongoose model in detail. "
            "What are the schema fields? How is the connection managed?"
        )
        print(result.text)
        save_session(agent.session_id, phase=3)
        print("\nSession saved. Run again to continue to phase 3.")

    elif phase == 3:
        print("\nPhase 3: Generate recommendations...")
        result = await agent.run(
            "Based on your analysis in phases 1 and 2, provide a prioritized list "
            "of improvements for this codebase."
        )
        print(result.text)

        # Clean up session file
        SESSION_FILE.unlink(missing_ok=True)
        print("\nWorkflow complete. Session cleaned up.")


if __name__ == "__main__":
    asyncio.run(main())
