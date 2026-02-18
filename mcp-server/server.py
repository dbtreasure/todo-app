import os
from mcp.server.fastmcp import FastMCP

server = FastMCP("my-mcp-server")


@server.tool()
def get_database_records(table: str, limit: int = 10) -> list[dict]:
    """Fetch records from a database table."""
    # Credentials loaded from env, never passed by Claude
    db_connection = os.getenv("DB_CONNECTION")

    # Query the database
    results = query_database(db_connection, f"SELECT * FROM {table} LIMIT {limit}")

    # Return structured result
    return [dict(row) for row in results]


@server.tool()
def create_issue(title: str, description: str, labels: list[str] | None = None) -> dict:
    """Create an issue in external tracking system."""
    # Handle credentials securely
    api_token = os.getenv("ISSUE_TRACKER_TOKEN")

    # Make API call
    issue = create_issue_in_system(api_token, title, description, labels)

    return {
        "id": issue["id"],
        "url": issue["url"],
        "status": "created",
    }


def query_database(connection_string: str, query: str) -> list:
    """Placeholder for actual database query implementation."""
    raise NotImplementedError("Replace with actual database driver")


def create_issue_in_system(
    token: str, title: str, description: str, labels: list[str] | None
) -> dict:
    """Placeholder for actual issue tracker API call."""
    raise NotImplementedError("Replace with actual API integration")


if __name__ == "__main__":
    server.run()
