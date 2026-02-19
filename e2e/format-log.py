#!/usr/bin/env python3
"""
Format Claude Agent SDK session logs into readable terminal-style transcripts.

Usage:
    python3 format-log.py <session.jsonl>
    python3 format-log.py logs/projects/-tmp-work/*.jsonl
"""

import json
import sys
import textwrap
from pathlib import Path

DIVIDER = "═" * 72
THIN = "─" * 72


def format_tool_result(content):
    """Format tool result content, truncating long outputs."""
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "tool_result":
                parts.append(item.get("content", ""))
            else:
                parts.append(str(item))
        content = "\n".join(parts)
    if not isinstance(content, str):
        content = str(content)
    lines = content.split("\n")
    if len(lines) > 20:
        return "\n".join(lines[:18]) + f"\n    ... ({len(lines) - 18} more lines)"
    return content


def format_session(filepath):
    """Parse a JSONL session file and print a readable transcript."""
    messages = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                messages.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    # Extract metadata from first messages
    session_id = None
    branch = None
    model = None

    for msg in messages:
        if not session_id:
            session_id = msg.get("sessionId")
        if not branch:
            branch = msg.get("gitBranch")
        if not model and msg.get("message", {}).get("model"):
            model = msg["message"]["model"]

    print(DIVIDER)
    print(f"  Session: {session_id or 'unknown'}")
    print(f"  Branch:  {branch or 'unknown'}")
    print(f"  Model:   {model or 'unknown'}")
    print(DIVIDER)
    print()

    for msg in messages:
        msg_type = msg.get("type")

        # Skip queue operations and internal messages
        if msg_type in ("queue-operation",):
            continue

        # User prompt
        if msg_type == "user":
            content = msg.get("message", {}).get("content", "")
            if isinstance(content, str) and content:
                print(f"  > {content}")
                print()
            elif isinstance(content, list):
                # Tool results
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "tool_result":
                        result_text = item.get("content", "")
                        if result_text:
                            indented = textwrap.indent(
                                format_tool_result(result_text), "    "
                            )
                            print(f"  ← result:")
                            print(indented)
                            print()

        # Assistant messages
        elif msg_type == "assistant":
            content_blocks = msg.get("message", {}).get("content", [])
            for block in content_blocks:
                block_type = block.get("type")

                if block_type == "thinking":
                    thinking = block.get("thinking", "")
                    if thinking:
                        # Show first 3 lines of thinking
                        lines = thinking.strip().split("\n")
                        preview = "\n    ".join(lines[:3])
                        suffix = (
                            f"\n    ... ({len(lines) - 3} more lines)"
                            if len(lines) > 3
                            else ""
                        )
                        print(f"  💭 thinking:")
                        print(f"    {preview}{suffix}")
                        print()

                elif block_type == "tool_use":
                    name = block.get("name", "?")
                    inp = block.get("input", {})
                    # Format input nicely
                    if len(inp) == 1:
                        key, val = next(iter(inp.items()))
                        print(f"  🔧 {name}  {key}={json.dumps(val)}")
                    else:
                        print(f"  🔧 {name}")
                        for k, v in inp.items():
                            val_str = json.dumps(v)
                            if len(val_str) > 100:
                                val_str = val_str[:97] + "..."
                            print(f"      {k}: {val_str}")
                    print()

                elif block_type == "text":
                    text = block.get("text", "")
                    if text:
                        print(THIN)
                        print(textwrap.indent(text.strip(), "  "))
                        print(THIN)
                        print()

        # Result message
        elif msg_type == "result":
            cost = msg.get("total_cost_usd", 0)
            duration = msg.get("duration_ms", 0)
            turns = msg.get("num_turns", 0)
            session = msg.get("session_id", "")
            is_error = msg.get("is_error", False)
            subtype = msg.get("subtype", "")

            print()
            print(DIVIDER)
            if is_error:
                print(f"  ❌ ERROR ({subtype})")
                for err in msg.get("errors", []):
                    print(f"     {err}")
            else:
                print(f"  ✅ Success")
            print(f"  Cost:     ${cost:.4f}")
            print(f"  Duration: {duration}ms")
            print(f"  Turns:    {turns}")
            print(f"  Session:  {session}")
            print(DIVIDER)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <session.jsonl> [session2.jsonl ...]")
        sys.exit(1)

    for i, filepath in enumerate(sys.argv[1:]):
        if i > 0:
            print("\n\n")
        format_session(filepath)
