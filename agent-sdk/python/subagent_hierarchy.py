"""
Subagent Hierarchy — Parallel Specialist Reviewers

Demonstrates a coordinator agent that spawns specialized child agents
to review code in parallel, then synthesizes their findings.

Architecture:
  Coordinator
  ├── SecurityReviewer  (scans for vulnerabilities)
  ├── PerformanceReviewer  (identifies bottlenecks)
  └── StyleReviewer  (checks code quality and consistency)

Usage:
    uv run agent-sdk/python/subagent_hierarchy.py
"""

import asyncio

from dotenv import load_dotenv

from claude_code_sdk import ClaudeCodeAgent, AgentConfig

load_dotenv()


async def run_specialist(name: str, system_prompt: str, task: str) -> dict:
    """Run a specialist reviewer agent."""
    print(f"  Starting {name}...")

    agent = ClaudeCodeAgent(
        config=AgentConfig(
            model="haiku",  # Use haiku for cost-efficient specialist work
            permission_mode="read-only",
            max_turns=5,
        ),
        system_prompt=system_prompt,
    )

    result = await agent.run(task)
    print(f"  {name} complete ({result.usage.output_tokens} output tokens)")

    return {
        "reviewer": name,
        "findings": result.text,
        "tokens": result.usage.input_tokens + result.usage.output_tokens,
    }


async def main():
    target = "src/lib/actions.ts"

    specialists = {
        "SecurityReviewer": (
            "You are a security specialist. Review code for vulnerabilities: "
            "injection attacks, authentication issues, data exposure, input validation gaps. "
            "Report findings with severity levels."
        ),
        "PerformanceReviewer": (
            "You are a performance specialist. Review code for bottlenecks: "
            "unnecessary database queries, missing caching opportunities, "
            "expensive operations, memory leaks. Report with impact estimates."
        ),
        "StyleReviewer": (
            "You are a code quality specialist. Review for style and maintainability: "
            "naming conventions, code duplication, complexity, error handling patterns, "
            "TypeScript best practices. Report with improvement suggestions."
        ),
    }

    task = f"Review the file at {target} and report your findings."

    # Run all specialists in parallel
    print("Running specialist reviewers in parallel...")
    results = await asyncio.gather(*[
        run_specialist(name, prompt, task)
        for name, prompt in specialists.items()
    ])

    # Synthesize findings with a coordinator
    print("\nSynthesizing findings with coordinator...")
    findings_summary = "\n\n".join([
        f"=== {r['reviewer']} ===\n{r['findings']}"
        for r in results
    ])

    coordinator = ClaudeCodeAgent(
        config=AgentConfig(
            model="sonnet",  # Use sonnet for synthesis
            permission_mode="read-only",
            max_turns=3,
        ),
        system_prompt=(
            "You are a senior tech lead. Synthesize findings from multiple "
            "specialist reviewers into a single, prioritized report. "
            "Deduplicate overlapping findings and rank by impact."
        ),
    )

    final = await coordinator.run(
        f"Synthesize these specialist review findings into a prioritized report:\n\n"
        f"{findings_summary}"
    )

    total_tokens = sum(r["tokens"] for r in results) + final.usage.input_tokens + final.usage.output_tokens
    print(f"\n{'=' * 60}")
    print(f"FINAL REPORT (total tokens: {total_tokens})")
    print(f"{'=' * 60}")
    print(final.text)


if __name__ == "__main__":
    asyncio.run(main())
