"""
Role-Based Access Control (RBAC) Permissions

Demonstrates configuring agent permissions based on user roles:
- Viewer: read-only access
- Developer: read + write to src/
- Admin: full access

Usage:
    uv run agent-sdk/python/role_based_permissions.py
"""

import asyncio
from dataclasses import dataclass, field

from dotenv import load_dotenv

from claude_code_sdk import ClaudeCodeAgent, AgentConfig, PermissionRequest

load_dotenv()


@dataclass
class Role:
    name: str
    allowed_tools: set[str]
    allowed_paths: set[str] = field(default_factory=set)
    denied_paths: set[str] = field(default_factory=set)
    allowed_bash_prefixes: list[str] = field(default_factory=list)


ROLES = {
    "viewer": Role(
        name="viewer",
        allowed_tools={"Read", "Grep", "Glob"},
    ),
    "developer": Role(
        name="developer",
        allowed_tools={"Read", "Grep", "Glob", "Edit", "Write", "Bash"},
        allowed_paths={"src/", "tests/"},
        denied_paths={".env", "infrastructure/"},
        allowed_bash_prefixes=["npm test", "npm run lint", "npx tsc", "npx prettier"],
    ),
    "admin": Role(
        name="admin",
        allowed_tools={"Read", "Grep", "Glob", "Edit", "Write", "Bash"},
        allowed_paths={""},  # empty string = all paths
        denied_paths={".env.production"},
        allowed_bash_prefixes=[],  # empty = all commands
    ),
}


def create_permission_handler(role: Role):
    """Create a permission handler for a specific role."""

    def handler(request: PermissionRequest) -> bool:
        tool = request.tool_name

        # Check tool allowlist
        if tool not in role.allowed_tools:
            return False

        # Check file path restrictions for file-based tools
        if tool in {"Read", "Edit", "Write"}:
            file_path = request.tool_input.get("file_path", "")

            # Check denied paths
            for denied in role.denied_paths:
                if denied and file_path.startswith(denied):
                    return False

            # Check allowed paths (empty string means all paths allowed)
            if role.allowed_paths and "" not in role.allowed_paths:
                return any(
                    file_path.startswith(prefix)
                    for prefix in role.allowed_paths
                )

        # Check bash restrictions
        if tool == "Bash" and role.allowed_bash_prefixes:
            command = request.tool_input.get("command", "")
            return any(
                command.startswith(prefix)
                for prefix in role.allowed_bash_prefixes
            )

        return True

    return handler


async def run_with_role(role_name: str, task: str):
    """Run an agent with a specific role's permissions."""
    role = ROLES[role_name]
    print(f"\n--- Running as {role.name} ---")

    agent = ClaudeCodeAgent(
        config=AgentConfig(
            model="sonnet",
            permission_mode="delegate",
            max_turns=5,
        ),
        permission_callback=create_permission_handler(role),
    )

    result = await agent.run(task)
    print(result.text)


if __name__ == "__main__":
    task = "Read src/lib/actions.ts and suggest improvements."

    # Run the same task with different roles to demonstrate access differences
    asyncio.run(run_with_role("viewer", task))
