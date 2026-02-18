"""
Internal API MCP Server — exposes database records and issue tracking to Claude Code.

Run with: uv run mcp-server/server.py
"""

import os
from typing import Optional

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

server = FastMCP("internal-api")


class QueryFilters(BaseModel):
    table: str = Field(..., description="Database table name")
    columns: list[str] = Field(default=["*"], description="Columns to select")
    limit: int = Field(default=100, ge=1, le=1000, description="Row limit")


@server.tool()
async def get_database_records(filters: QueryFilters) -> dict:
    """Fetch records from the internal database via the API."""
    api_url = os.environ["INTERNAL_API_URL"]
    api_token = os.environ["INTERNAL_API_TOKEN"]

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{api_url}/query",
            headers={"Authorization": f"Bearer {api_token}"},
            params={
                "table": filters.table,
                "columns": ",".join(filters.columns),
                "limit": filters.limit,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()

    return {
        "table": filters.table,
        "row_count": len(data.get("rows", [])),
        "rows": data.get("rows", []),
    }


@server.tool()
async def create_issue(
    title: str,
    description: str,
    labels: Optional[list[str]] = None,
    priority: str = "medium",
) -> dict:
    """Create an issue in the internal tracking system."""
    api_url = os.environ["INTERNAL_API_URL"]
    api_token = os.environ["INTERNAL_API_TOKEN"]

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{api_url}/issues",
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
            },
            json={
                "title": title,
                "description": description,
                "labels": labels or [],
                "priority": priority,
            },
            timeout=30.0,
        )
        response.raise_for_status()
        issue = response.json()

    return {
        "id": issue["id"],
        "url": issue["url"],
        "status": "created",
    }


if __name__ == "__main__":
    server.run()
