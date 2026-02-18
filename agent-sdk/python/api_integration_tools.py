"""
API Integration Tools — Customer Data and Invoicing

Demonstrates real-world custom tools that integrate with external APIs.
Shows how to handle authentication, errors, and structured responses.

Usage:
    uv run agent-sdk/python/api_integration_tools.py
"""

import asyncio
import os

import httpx
from dotenv import load_dotenv

from claude_code_sdk import ClaudeCodeAgent, AgentConfig, Tool, ToolResult

load_dotenv()


# Define tools
get_customer_tool = Tool(
    name="get_customer_data",
    description="Look up customer information by ID. Returns name, email, plan, and account status.",
    input_schema={
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "The unique customer identifier",
            }
        },
        "required": ["customer_id"],
    },
)

create_invoice_tool = Tool(
    name="create_invoice",
    description="Create a new invoice for a customer. Returns the invoice ID and total.",
    input_schema={
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "The customer to invoice",
            },
            "items": {
                "type": "array",
                "description": "Line items for the invoice",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "quantity": {"type": "integer", "minimum": 1},
                        "unit_price": {"type": "number", "minimum": 0},
                    },
                    "required": ["description", "quantity", "unit_price"],
                },
            },
        },
        "required": ["customer_id", "items"],
    },
)


async def handle_tool(name: str, tool_input: dict) -> ToolResult:
    """Route tool calls to their handlers."""
    api_url = os.environ.get("BILLING_API_URL", "https://api.example.com")
    api_key = os.environ.get("BILLING_API_KEY", "")

    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

        try:
            if name == "get_customer_data":
                response = await client.get(
                    f"{api_url}/customers/{tool_input['customer_id']}",
                    headers=headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                return ToolResult(output=response.text)

            elif name == "create_invoice":
                response = await client.post(
                    f"{api_url}/invoices",
                    json=tool_input,
                    headers=headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                return ToolResult(output=response.text)

            else:
                return ToolResult(error=f"Unknown tool: {name}")

        except httpx.HTTPStatusError as e:
            return ToolResult(error=f"API error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            return ToolResult(error=f"Connection error: {e}")


async def main():
    agent = ClaudeCodeAgent(
        config=AgentConfig(
            model="sonnet",
            permission_mode="read-only",
            max_turns=10,
        ),
        custom_tools=[get_customer_tool, create_invoice_tool],
        tool_handler=lambda name, input: asyncio.get_event_loop().run_until_complete(
            handle_tool(name, input)
        ),
    )

    result = await agent.run(
        "Look up customer CUST-001 and create an invoice for them with "
        "2 hours of consulting at $150/hr and 1 deployment setup at $500."
    )

    print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
