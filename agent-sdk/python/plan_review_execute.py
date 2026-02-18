"""
Three-Agent Pattern: Plan -> Review -> Execute

Demonstrates separation of concerns in agent architectures:
1. Planner agent creates an implementation plan
2. Reviewer agent evaluates the plan for issues
3. Executor agent implements the approved plan

Usage:
    uv run agent-sdk/python/plan_review_execute.py
"""

import asyncio

from claude_code_sdk import ClaudeCodeAgent, AgentConfig


async def plan_review_execute(task: str) -> dict:
    """Run the three-agent workflow."""

    # Phase 1: Plan
    print("Phase 1: Planning...")
    planner = ClaudeCodeAgent(
        config=AgentConfig(
            model="sonnet",
            permission_mode="read-only",
            max_turns=5,
        ),
        system_prompt=(
            "You are a planning agent. Given a task, create a detailed implementation plan. "
            "List specific files to change, what changes to make, and potential risks. "
            "Do NOT implement anything — only plan."
        ),
    )

    plan_result = await planner.run(f"Create an implementation plan for: {task}")
    plan = plan_result.text
    print(f"  Plan created ({len(plan)} chars)")

    # Phase 2: Review
    print("Phase 2: Reviewing...")
    reviewer = ClaudeCodeAgent(
        config=AgentConfig(
            model="sonnet",
            permission_mode="read-only",
            max_turns=5,
        ),
        system_prompt=(
            "You are a code review agent. Review implementation plans for issues: "
            "missing edge cases, security concerns, performance problems, or scope creep. "
            "Approve the plan or request specific changes."
        ),
    )

    review_result = await reviewer.run(
        f"Review this implementation plan:\n\n{plan}\n\nApprove or request changes."
    )
    review = review_result.text
    print(f"  Review complete ({len(review)} chars)")

    # Phase 3: Execute (only if approved)
    if "approve" in review.lower() or "approved" in review.lower():
        print("Phase 3: Executing...")
        executor = ClaudeCodeAgent(
            config=AgentConfig(
                model="sonnet",
                permission_mode="workspace",
                max_turns=15,
            ),
            system_prompt=(
                "You are an implementation agent. Execute the provided plan exactly. "
                "Make the specified changes, run tests, and report results."
            ),
        )

        exec_result = await executor.run(
            f"Execute this approved plan:\n\n{plan}"
        )
        return {"plan": plan, "review": review, "execution": exec_result.text}
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
