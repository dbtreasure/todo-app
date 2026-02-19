"""
API Integration Tools -- Customer Data and Invoicing

Demonstrates real-world custom tools that integrate with external APIs
using httpx. Shows two tools registered via @tool decorator, served
through create_sdk_mcp_server, and invoked by ClaudeSDKClient.

Usage:
    uv run agent-sdk/python/api_integration_tools.py
"""

import asyncio
import json
import os
import sys

import httpx
from dotenv import load_dotenv

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    ResultMessage,
    TextBlock,
    create_sdk_mcp_server,
    tool,
)

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

API_BASE_URL = os.environ.get("BILLING_API_URL", "https://httpbin.org")
API_KEY = os.environ.get("BILLING_API_KEY", "")


@tool(
    "get_customer_data",
    "Look up customer information by ID. Returns name, email, plan, and account status.",
    {"customer_id": str},
)
def get_customer_data(customer_id: str) -> dict:
    """Fetch customer data from the billing API."""
    headers = {"Authorization": f"Bearer {API_KEY}"} if API_KEY else {}

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.get(
                f"{API_BASE_URL}/anything/customers/{customer_id}",
                headers=headers,
            )
            response.raise_for_status()
            return {
                "content": [{"type": "text", "text": response.text}]
            }
    except httpx.HTTPStatusError as e:
        return {
            "content": [
                {"type": "text", "text": f"API error {e.response.status_code}: {e.response.text}"}
            ]
        }
    except httpx.RequestError as e:
        return {
            "content": [{"type": "text", "text": f"Connection error: {e}"}]
        }


@tool(
    "create_invoice",
    "Create a new invoice for a customer with line items. Returns the invoice ID and total.",
    {"customer_id": str, "items": list},
)
def create_invoice(customer_id: str, items: list) -> dict:
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
            return {
                "content": [{"type": "text", "text": response.text}]
            }
    except httpx.HTTPStatusError as e:
        return {
            "content": [
                {"type": "text", "text": f"API error {e.response.status_code}: {e.response.text}"}
            ]
        }
    except httpx.RequestError as e:
        return {
            "content": [{"type": "text", "text": f"Connection error: {e}"}]
        }


server = create_sdk_mcp_server(
    name="service", tools=[get_customer_data, create_invoice]
)


async def main():
    options = ClaudeAgentOptions(
        mcp_servers={"service": server},
        allowed_tools=["mcp__service__get_customer_data", "mcp__service__create_invoice"],
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
    )

    client = ClaudeSDKClient(options)

    async for message in client.process(
        "Look up customer CUST-001 and create an invoice for them with "
        "2 hours of consulting at $150/hr and 1 deployment setup at $500."
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"Session: {message.session_id}")


if __name__ == "__main__":
    asyncio.run(main())
