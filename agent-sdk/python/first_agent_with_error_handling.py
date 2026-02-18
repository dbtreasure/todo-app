"""
First Agent with Error Handling

Demonstrates proper error handling, logging, and graceful failure.

Usage:
    uv run agent-sdk/python/first_agent_with_error_handling.py
"""

import asyncio
import logging
import sys

from dotenv import load_dotenv

from claude_code_sdk import ClaudeCodeAgent, AgentConfig
from claude_code_sdk.exceptions import AgentError, AuthenticationError, RateLimitError

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting agent...")

    try:
        agent = ClaudeCodeAgent(
            config=AgentConfig(
                model="sonnet",
                permission_mode="read-only",
                max_turns=5,
            ),
        )

        result = await agent.run(
            "Read src/lib/actions.ts and explain what each server action does."
        )

        logger.info(
            "Agent completed. Tokens: %d in, %d out",
            result.usage.input_tokens,
            result.usage.output_tokens,
        )
        print(result.text)

    except AuthenticationError:
        logger.error("Authentication failed. Check your ANTHROPIC_API_KEY.")
        sys.exit(1)
    except RateLimitError:
        logger.error("Rate limited. Wait and try again.")
        sys.exit(1)
    except AgentError as e:
        logger.error("Agent error: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
