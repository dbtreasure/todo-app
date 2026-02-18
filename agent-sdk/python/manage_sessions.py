"""
Session Management — Create, List, and Clean Up Sessions

Demonstrates programmatic session lifecycle management.

Usage:
    uv run agent-sdk/python/manage_sessions.py
"""

import asyncio

from dotenv import load_dotenv

from claude_code_sdk import ClaudeCodeAgent, AgentConfig, SessionManager

load_dotenv()


async def main():
    manager = SessionManager()

    # List existing sessions
    print("=== Existing Sessions ===")
    sessions = await manager.list_sessions()
    for session in sessions:
        print(f"  {session.id} | created: {session.created_at} | turns: {session.turn_count}")

    if not sessions:
        print("  No sessions found.")

    # Create a new session
    print("\n=== Creating New Session ===")
    agent = ClaudeCodeAgent(
        config=AgentConfig(
            model="sonnet",
            permission_mode="read-only",
            max_turns=3,
        ),
    )
    result = await agent.run("What files are in the src/ directory?")
    print(f"  Session ID: {agent.session_id}")
    print(f"  Response: {result.text[:200]}...")

    # Clean up old sessions (older than 7 days)
    print("\n=== Cleaning Up Old Sessions ===")
    cleaned = await manager.cleanup(max_age_days=7)
    print(f"  Cleaned up {cleaned} old session(s).")


if __name__ == "__main__":
    asyncio.run(main())
