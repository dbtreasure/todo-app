"""
User Service MCP Server

A production-grade MCP server that exposes user management operations.
Demonstrates security-first design: input validation, credential isolation,
error handling, and audit logging.

Usage:
    uv run mcp-server/user_service.py
"""

# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "mcp>=1.0.0",
#     "httpx>=0.27.0",
#     "pydantic>=2.0.0",
# ]
# ///

import logging
import os

import httpx
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = FastMCP("user-service")


# ── Input Models ──────────────────────────────────────────────────

class GetUserRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=50, description="User ID to look up")

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        if not all(c.isalnum() or c in '-_' for c in v):
            raise ValueError("user_id must be alphanumeric (hyphens and underscores allowed)")
        return v


class ListUsersRequest(BaseModel):
    department: str = Field(..., min_length=1, max_length=100, description="Department name")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum users to return")


# ── Credential Management ────────────────────────────────────────

def get_api_config() -> tuple[str, str]:
    """Load API credentials from environment. Never expose to the model."""
    api_url = os.environ.get("INTERNAL_API_URL")
    api_token = os.environ.get("INTERNAL_API_TOKEN")

    if not api_url or not api_token:
        raise ValueError(
            "INTERNAL_API_URL and INTERNAL_API_TOKEN must be set. "
            "These credentials are loaded from the environment and never exposed to Claude."
        )

    return api_url, api_token


# ── Tools ─────────────────────────────────────────────────────────

@server.tool()
async def get_user(user_id: str) -> dict:
    """Look up a user by their unique identifier.

    Returns user profile information including name, email, department, and role.
    Credentials are loaded from environment variables and never seen by the model.
    """
    request = GetUserRequest(user_id=user_id)
    api_url, api_token = get_api_config()

    logger.info(f"Looking up user: {request.user_id}")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{api_url}/users/{request.user_id}",
                headers={"Authorization": f"Bearer {api_token}"},
                timeout=10.0,
            )
            response.raise_for_status()
            user_data = response.json()

            return {
                "user_id": user_data.get("id"),
                "name": user_data.get("name"),
                "email": user_data.get("email"),
                "department": user_data.get("department"),
                "role": user_data.get("role"),
                "active": user_data.get("active", True),
            }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"error": "User not found", "user_id": request.user_id}
            return {"error": f"API error: {e.response.status_code}"}
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            return {"error": "Failed to connect to user service"}


@server.tool()
async def list_users_by_department(department: str) -> dict:
    """List all users in a specific department.

    Returns a list of users filtered by department name.
    Supports pagination via the limit parameter.
    """
    request = ListUsersRequest(department=department)
    api_url, api_token = get_api_config()

    logger.info(f"Listing users in department: {request.department} (limit: {request.limit})")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{api_url}/users",
                params={"department": request.department, "limit": request.limit},
                headers={"Authorization": f"Bearer {api_token}"},
                timeout=10.0,
            )
            response.raise_for_status()
            data = response.json()

            users = [
                {
                    "user_id": u.get("id"),
                    "name": u.get("name"),
                    "role": u.get("role"),
                }
                for u in data.get("users", [])
            ]

            return {
                "department": request.department,
                "count": len(users),
                "users": users,
            }

        except httpx.HTTPStatusError as e:
            return {"error": f"API error: {e.response.status_code}"}
        except httpx.RequestError as e:
            logger.error(f"Request failed: {e}")
            return {"error": "Failed to connect to user service"}


if __name__ == "__main__":
    server.run()
