"""
First Agent with Error Handling

Demonstrates proper error handling, logging, and graceful failure
using the Claude Agent SDK.

Usage:
    uv run agent-sdk/python/first_agent_with_error_handling.py
"""

import asyncio
import logging
import sys

from dotenv import load_dotenv

from claude_agent_sdk import (
    AssistantMessage,
    CLIJSONDecodeError,
    CLINotFoundError,
    ClaudeAgentOptions,
    ClaudeSDKError,
    ProcessError,
    ResultMessage,
    TextBlock,
    query,
)

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting agent...")

    try:
        options = ClaudeAgentOptions(
            permission_mode="bypassPermissions",
            model="claude-sonnet-4-5",
            max_turns=5,
        )

        async for message in query(
            prompt="Read src/lib/actions.ts and explain what each server action does.",
            options=options,
        ):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)
            elif isinstance(message, ResultMessage):
                logger.info(
                    "Agent completed. Cost: $%.4f, Duration: %dms",
                    message.cost_usd,
                    message.duration_ms,
                )

    except CLINotFoundError:
        logger.error(
            "Claude CLI not found. Ensure it is installed and on your PATH."
        )
        sys.exit(1)
    except ProcessError as e:
        logger.error("Process error: %s", e)
        sys.exit(1)
    except CLIJSONDecodeError as e:
        logger.error("Failed to decode CLI JSON output: %s", e)
        sys.exit(1)
    except ClaudeSDKError as e:
        logger.error("SDK error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
