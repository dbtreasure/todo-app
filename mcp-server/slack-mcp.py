"""
Slack MCP Server — read-only access to Slack channels and threads.

Exposes tools for Claude Code to read channel history and thread replies.
Requires a Slack Bot Token with channels:history and channels:read scopes.

Usage:
    uv run mcp-server/slack-mcp.py
"""

import os

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

server = FastMCP("slack-reader")


def get_slack_client() -> WebClient:
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        raise ValueError("SLACK_BOT_TOKEN environment variable is required")
    return WebClient(token=token)


class ChannelRequest(BaseModel):
    channel_id: str = Field(..., description="Slack channel ID (e.g., C01234567)")
    limit: int = Field(default=20, ge=1, le=100, description="Number of messages to fetch")


class ThreadRequest(BaseModel):
    channel_id: str = Field(..., description="Slack channel ID")
    thread_ts: str = Field(..., description="Thread timestamp (ts) of the parent message")
    limit: int = Field(default=50, ge=1, le=200, description="Number of replies to fetch")


@server.tool()
def read_channel(request: ChannelRequest) -> dict:
    """Read recent messages from a Slack channel.

    Returns the most recent messages with timestamps, authors, and text content.
    Requires the bot to be a member of the channel.
    """
    client = get_slack_client()

    try:
        response = client.conversations_history(
            channel=request.channel_id,
            limit=request.limit,
        )

        messages = []
        for msg in response.get("messages", []):
            messages.append({
                "ts": msg.get("ts"),
                "user": msg.get("user", "unknown"),
                "text": msg.get("text", ""),
                "has_thread": bool(msg.get("thread_ts")),
                "reply_count": msg.get("reply_count", 0),
            })

        return {
            "channel": request.channel_id,
            "message_count": len(messages),
            "messages": messages,
        }

    except SlackApiError as e:
        return {
            "error": str(e.response["error"]),
            "channel": request.channel_id,
        }


@server.tool()
def read_thread(request: ThreadRequest) -> dict:
    """Read replies in a Slack thread.

    Returns all replies to a specific message thread.
    """
    client = get_slack_client()

    try:
        response = client.conversations_replies(
            channel=request.channel_id,
            ts=request.thread_ts,
            limit=request.limit,
        )

        replies = []
        for msg in response.get("messages", []):
            replies.append({
                "ts": msg.get("ts"),
                "user": msg.get("user", "unknown"),
                "text": msg.get("text", ""),
            })

        return {
            "channel": request.channel_id,
            "thread_ts": request.thread_ts,
            "reply_count": len(replies),
            "replies": replies,
        }

    except SlackApiError as e:
        return {
            "error": str(e.response["error"]),
            "channel": request.channel_id,
            "thread_ts": request.thread_ts,
        }


if __name__ == "__main__":
    server.run()
