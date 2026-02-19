"""
API Integration Tools -- Customer Data and Invoicing

Demonstrates real-world custom tools that integrate with external APIs
using httpx. Two tools are registered in a FastMCP server, served as a
subprocess via mcp_servers in ClaudeAgentOptions, and invoked through
the SDK's query() function.

Usage:
    cd /tmp/work
    uv venv /tmp/py-env && source /tmp/py-env/bin/activate
    uv pip install claude-agent-sdk mcp python-dotenv httpx
    python3 agent-sdk/python/api_integration_tools.py
"""

import asyncio
import os
import sys

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

API_BASE_URL = os.environ.get("BILLING_API_URL", "https://httpbin.org")
API_KEY = os.environ.get("BILLING_API_KEY", "")


# ---------------------------------------------------------------------------
# 1. Build an MCP server with two API-backed tools
# ---------------------------------------------------------------------------

mcp = FastMCP("service")


@mcp.tool(
    name="get_customer_data",
    description="Look up customer information by ID. Returns name, email, plan, and account status.",
)
def get_customer_data(customer_id: str) -> str:
    """Fetch customer data from the billing API."""
    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                f"{API_BASE_URL}/anything/customers/{customer_id}",
                headers=headers,
            )
            response.raise_for_status()
            return response.text
    except httpx.HTTPStatusError as e:
        return f"API error {e.response.status_code}: {e.response.text}"
    except httpx.RequestError as e:
        return f"Connection error: {e}"


@mcp.tool(
    name="create_invoice",
    description="Create a new invoice for a customer with line items. Returns the invoice ID and total.",
)
def create_invoice(customer_id: str, items: list) -> str:
    """Create an invoice via the billing API."""
    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}

    payload = {
        "customer_id": customer_id,
        "items": items,
    }

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{API_BASE_URL}/anything/invoices",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.text
    except httpx.HTTPStatusError as e:
        return f"API error {e.response.status_code}: {e.response.text}"
    except httpx.RequestError as e:
        return f"Connection error: {e}"


# ---------------------------------------------------------------------------
# 2. Use the SDK to run a prompt with the custom tools
# ---------------------------------------------------------------------------


async def main():
    script_path = os.path.abspath(__file__)

    options = ClaudeAgentOptions(
        cwd="/tmp/work",
        mcp_servers={
            "service": {
                "command": sys.executable,
                "args": ["-m", "mcp.server.fastmcp", "run", script_path],
            },
        },
        allowed_tools=[
            "mcp__service__get_customer_data",
            "mcp__service__create_invoice",
        ],
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
    )

    async for message in query(
        prompt=(
            "Look up customer CUST-001 and create an invoice for them with "
            "2 hours of consulting at $150/hr and 1 deployment setup at $500."
        ),
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"\nSession: {message.session_id}")


if __name__ == "__main__":
    asyncio.run(main())
