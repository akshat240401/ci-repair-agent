from __future__ import annotations

from pathlib import Path

from src.tools.repo_tools import (
    ToolError,
    get_test_definition,
    list_directory_limited,
    read_code_chunk,
    read_config,
    search_symbol,
    search_text,
)


MAX_TOOL_CALLS = 12


def execute_tool(repo_dir: Path, tool: str, arguments: dict) -> str:
    try:
        if tool == "read_code_chunk":
            return read_code_chunk(repo_dir, **arguments)
        if tool == "search_text":
            return search_text(repo_dir, **arguments)
        if tool == "search_symbol":
            return search_symbol(repo_dir, **arguments)
        if tool == "get_test_definition":
            return get_test_definition(repo_dir, **arguments)
        if tool == "list_directory_limited":
            return list_directory_limited(repo_dir, **arguments)
        if tool == "read_config":
            return read_config(repo_dir, **arguments)
        return f"TOOL_ERROR: unknown tool {tool}"
    except (ToolError, TypeError) as exc:
        return f"TOOL_ERROR: {exc}"
