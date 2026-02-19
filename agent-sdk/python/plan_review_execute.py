"""
Three-Agent Pattern: Plan -> Review -> Execute

Demonstrates separation of concerns in agent architectures:
1. Planner agent creates an implementation plan (read-only tools)
2. Reviewer agent evaluates the plan for issues (read-only tools)
3. Executor agent implements the approved plan (read+write tools)

Usage:
    uv run agent-sdk/python/plan_review_execute.py
"""

import sys
import asyncio

from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def _collect_text(prompt: str, options: ClaudeAgentOptions) -> str:
    """Run a query and collect all text blocks into a single string."""
    parts: list[str] = []
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    parts.append(block.text)
        elif isinstance(message, ResultMessage):
            print(f"  Cost: ${message.cost_usd:.4f} | Duration: {message.duration_ms}ms")
    return "\n".join(parts)


async def plan_review_execute(task: str) -> dict:
    """Run the three-agent workflow."""

    # Phase 1: Plan (read-only analysis)
    print("Phase 1: Planning...")
    planner_options = ClaudeAgentOptions(
        permission_mode="plan",
        allowed_tools=["Read", "Grep", "Glob"],
        model="claude-sonnet-4-5",
    )
    plan_prompt = (
        "You are a planning agent. Given a task, create a detailed implementation plan. "
        "List specific files to change, what changes to make, and potential risks. "
        "Do NOT implement anything -- only plan.\n\n"
        f"Create an implementation plan for: {task}"
    )
    plan = await _collect_text(plan_prompt, planner_options)
    print(f"  Plan created ({len(plan)} chars)")

    # Phase 2: Review (read-only analysis)
    print("Phase 2: Reviewing...")
    reviewer_options = ClaudeAgentOptions(
        permission_mode="plan",
        allowed_tools=["Read", "Grep", "Glob"],
        model="claude-sonnet-4-5",
    )
    review_prompt = (
        "You are a code review agent. Review implementation plans for issues: "
        "missing edge cases, security concerns, performance problems, or scope creep. "
        "Approve the plan or request specific changes.\n\n"
        f"Review this implementation plan:\n\n{plan}\n\nApprove or request changes."
    )
    review = await _collect_text(review_prompt, reviewer_options)
    print(f"  Review complete ({len(review)} chars)")

    # Phase 3: Execute (only if the reviewer approved)
    if "approve" in review.lower() or "approved" in review.lower():
        print("Phase 3: Executing approved plan...")
        executor_options = ClaudeAgentOptions(
            permission_mode="acceptEdits",
            allowed_tools=["Read", "Edit", "Write", "Grep", "Glob"],
            model="claude-sonnet-4-5",
        )
        exec_prompt = (
            "You are an implementation agent. Execute the provided plan exactly. "
            "Make the specified changes, run tests, and report results.\n\n"
            f"Execute this approved plan:\n\n{plan}"
        )
        execution = await _collect_text(exec_prompt, executor_options)
        return {"plan": plan, "review": review, "execution": execution}
    else:
        print("  Plan was not approved. Returning review feedback.")
        return {"plan": plan, "review": review, "execution": None}


if __name__ == "__main__":
    task = "Add input validation to the createTodo server action in src/lib/actions.ts"
    result = asyncio.run(plan_review_execute(task))
    print("\n=== Results ===")
    for phase, output in result.items():
        status = "completed" if output else "skipped"
        print(f"  {phase}: {status}")
