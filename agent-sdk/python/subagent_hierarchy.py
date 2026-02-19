"""
Subagent Hierarchy -- Parallel Specialist Reviewers

Demonstrates a parent agent that orchestrates three specialist subagents
using AgentDefinition in ClaudeAgentOptions. The parent agent uses the
Task tool to invoke subagents, and subagents use Read/Glob/Grep to
inspect code.

Architecture:
  Parent (coordinator)
  +-- security_reviewer  (scans for vulnerabilities)
  +-- performance_reviewer  (identifies bottlenecks)
  +-- style_reviewer  (checks code quality and consistency)

Usage:
    uv run agent-sdk/python/subagent_hierarchy.py
"""

import asyncio
import sys

from dotenv import load_dotenv

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def main():
    options = ClaudeAgentOptions(
        cwd="/tmp/work",
        agents={
            "security_reviewer": AgentDefinition(
                description="Reviews code for security vulnerabilities",
                prompt=(
                    "You are a security specialist. Review code for vulnerabilities: "
                    "injection attacks, authentication issues, data exposure, input "
                    "validation gaps. Report findings with severity levels (critical, "
                    "high, medium, low). Use the Read, Glob, and Grep tools to "
                    "inspect the codebase."
                ),
                tools=["Read", "Glob", "Grep"],
                model="haiku",
            ),
            "performance_reviewer": AgentDefinition(
                description="Reviews code for performance bottlenecks",
                prompt=(
                    "You are a performance specialist. Review code for bottlenecks: "
                    "unnecessary database queries, missing caching opportunities, "
                    "expensive operations, memory leaks. Report with impact estimates "
                    "(high, medium, low). Use the Read, Glob, and Grep tools to "
                    "inspect the codebase."
                ),
                tools=["Read", "Glob", "Grep"],
                model="haiku",
            ),
            "style_reviewer": AgentDefinition(
                description="Reviews code for style and maintainability",
                prompt=(
                    "You are a code quality specialist. Review for style and "
                    "maintainability: naming conventions, code duplication, complexity, "
                    "error handling patterns, TypeScript best practices. Report with "
                    "improvement suggestions. Use the Read, Glob, and Grep tools to "
                    "inspect the codebase."
                ),
                tools=["Read", "Glob", "Grep"],
                model="haiku",
            ),
        },
        allowed_tools=["Read", "Glob", "Grep", "Task"],
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
    )

    async for message in query(
        prompt=(
            "You are a senior tech lead conducting a code review. Review the file "
            "src/lib/actions.ts by delegating to your three specialist subagents: "
            "security_reviewer, performance_reviewer, and style_reviewer. "
            "Each subagent should read and analyze the file independently. "
            "Once all three have reported back, synthesize their findings into a "
            "single prioritized report. Deduplicate overlapping findings and rank "
            "by impact."
        ),
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"Session: {message.session_id}")


if __name__ == "__main__":
    asyncio.run(main())
