import os
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from pymongo import MongoClient

server = FastMCP("todo-mcp-server")


def get_db():
    """Connect to the todo app's MongoDB database."""
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/todoDb")
    client = MongoClient(uri)
    return client.get_default_database()


@server.tool()
def get_todos(limit: int = 10) -> list[dict]:
    """Fetch todos from the todo app database, sorted newest first."""
    db = get_db()
    cursor = db.todos.find({}, {"_id": 0, "title": 1, "desc": 1, "createdAt": 1}).sort(
        "createdAt", -1
    ).limit(limit)
    return [
        {
            "title": doc.get("title", ""),
            "description": doc.get("desc", ""),
            "created": doc["createdAt"].isoformat() if isinstance(doc.get("createdAt"), datetime) else str(doc.get("createdAt", "")),
        }
        for doc in cursor
    ]


@server.tool()
def count_todos() -> dict:
    """Count total todos in the database."""
    db = get_db()
    total = db.todos.count_documents({})
    return {"total": total}


@server.tool()
def search_todos(query: str) -> list[dict]:
    """Search todos by title (case-insensitive substring match)."""
    db = get_db()
    cursor = db.todos.find(
        {"title": {"$regex": query, "$options": "i"}},
        {"_id": 0, "title": 1, "desc": 1},
    )
    return [{"title": doc.get("title", ""), "description": doc.get("desc", "")} for doc in cursor]


if __name__ == "__main__":
    server.run()
