"""
Role-Based Access Control (RBAC) Permissions

Demonstrates configuring agent permissions based on user roles using
dataclasses and the can_use_tool callback pattern.

Three tiers:
- Viewer: read-only access (Read, Grep, Glob)
- Developer: read + edit in src/ and tests/, safe bash commands only
- Admin: full access except .env.production

Usage:
    uv run agent-sdk/python/role_based_permissions.py
"""

import asyncio
import sys
from dataclasses import dataclass, field

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    PermissionResultAllow,
    PermissionResultDeny,
    ResultMessage,
    TextBlock,
    query,
)

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@dataclass
class Role:
    """Defines permissions for a given role."""

    name: str
    allowed_tools: set[str]
    allowed_paths: set[str] = field(default_factory=set)
    denied_paths: set[str] = field(default_factory=set)
    allowed_bash_prefixes: list[str] = field(default_factory=list)


ROLES: dict[str, Role] = {
    "viewer": Role(
        name="viewer",
        allowed_tools={"Read", "Grep", "Glob"},
    ),
    "developer": Role(
        name="developer",
        allowed_tools={"Read", "Grep", "Glob", "Edit", "Write", "Bash"},
        allowed_paths={"src/", "tests/"},
        denied_paths={".env", "infrastructure/"},
        allowed_bash_prefixes=[
            "npm test",
            "npm run lint",
            "npx tsc",
            "npx prettier",
        ],
    ),
    "admin": Role(
        name="admin",
        allowed_tools={"Read", "Grep", "Glob", "Edit", "Write", "Bash"},
        allowed_paths={""},  # empty string = all paths allowed
        denied_paths={".env.production"},
        allowed_bash_prefixes=[],  # empty = all commands allowed
    ),
}


def create_permission_handler(role: Role):
    """Create a can_use_tool handler bound to a specific role's permissions."""

    async def handler(
        tool_name: str, tool_input: dict, context: dict
    ) -> PermissionResultAllow | PermissionResultDeny:
        # Check tool allowlist
        if tool_name not in role.allowed_tools:
            return PermissionResultDeny(
                message=f"Role '{role.name}' cannot use tool '{tool_name}'"
            )

        # Check file path restrictions for file-based tools
        if tool_name in {"Read", "Edit", "Write"}:
            file_path = tool_input.get("file_path", "")

            # Check denied paths first
            for denied in role.denied_paths:
                if denied and file_path.startswith(denied):
                    return PermissionResultDeny(
                        message=f"Role '{role.name}' denied access to '{file_path}'"
                    )

            # Check allowed paths (empty string means all paths)
            if role.allowed_paths and "" not in role.allowed_paths:
                if not any(
                    file_path.startswith(prefix) for prefix in role.allowed_paths
                ):
                    return PermissionResultDeny(
                        message=(
                            f"Role '{role.name}' can only access paths: "
                            f"{', '.join(role.allowed_paths)}"
                        )
                    )

        # Check bash command restrictions
        if tool_name == "Bash" and role.allowed_bash_prefixes:
            command = tool_input.get("command", "")
            if not any(
                command.startswith(prefix) for prefix in role.allowed_bash_prefixes
            ):
                return PermissionResultDeny(
                    message=f"Role '{role.name}' cannot run bash command: '{command}'"
                )

        return PermissionResultAllow(updated_input=tool_input)

    return handler


async def run_with_role(role_name: str, task: str):
    """Run an agent with a specific role's permissions."""
    role = ROLES[role_name]
    print(f"\n--- Running as '{role.name}' ---")

    options = ClaudeAgentOptions(
        can_use_tool=create_permission_handler(role),
        permission_mode="default",
        model="claude-sonnet-4-5",
        max_turns=5,
    )

    async for message in query(prompt=task, options=options, cwd="/tmp/work"):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text, end="", flush=True)
        elif isinstance(message, ResultMessage):
            print(f"\n\nDone. Cost: ${message.total_cost_usd:.4f}")
            print(f"Duration: {message.duration_ms}ms")


if __name__ == "__main__":
    task = "Read src/lib/actions.ts and suggest improvements."

    # Run the same task with different roles to demonstrate access differences
    asyncio.run(run_with_role("viewer", task))
