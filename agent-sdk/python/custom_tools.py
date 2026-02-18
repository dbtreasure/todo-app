"""
Custom Tools — Fibonacci Calculator

Demonstrates defining a custom tool with JSON Schema input validation,
registering it with the agent, and handling tool calls.

Usage:
    uv run agent-sdk/python/custom_tools.py
"""

import asyncio

from dotenv import load_dotenv

from claude_code_sdk import ClaudeCodeAgent, AgentConfig, Tool, ToolResult

load_dotenv()


# Define a custom tool
fibonacci_tool = Tool(
    name="calculate_fibonacci",
    description="Calculate the nth Fibonacci number. Works for n between 0 and 50.",
    input_schema={
        "type": "object",
        "properties": {
            "n": {
                "type": "integer",
                "description": "The position in the Fibonacci sequence (0-indexed)",
                "minimum": 0,
                "maximum": 50,
            }
        },
        "required": ["n"],
    },
)


def handle_fibonacci(tool_input: dict) -> ToolResult:
    """Handle the calculate_fibonacci tool call."""
    n = tool_input["n"]

    if n <= 1:
        return ToolResult(output=str(n))

    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b

    return ToolResult(output=str(b))


async def main():
    agent = ClaudeCodeAgent(
        config=AgentConfig(
            model="sonnet",
            permission_mode="read-only",
            max_turns=5,
        ),
        custom_tools=[fibonacci_tool],
        tool_handler=lambda name, input: (
            handle_fibonacci(input) if name == "calculate_fibonacci"
            else ToolResult(error=f"Unknown tool: {name}")
        ),
    )

    result = await agent.run(
        "Calculate the 10th, 20th, and 30th Fibonacci numbers. "
        "Then explain the growth rate of the Fibonacci sequence."
    )

    print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
