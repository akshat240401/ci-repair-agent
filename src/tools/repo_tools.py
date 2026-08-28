from __future__ import annotations

import re
from pathlib import Path


ALLOWED_TEXT_SUFFIXES = {
    ".py", ".json", ".toml", ".yaml", ".yml", ".ini", ".cfg", ".txt"
}
CONFIG_SUFFIXES = {".json", ".toml", ".yaml", ".yml", ".ini", ".cfg"}
MAX_TOOL_CHARS = 8_000


class ToolError(RuntimeError):
    pass


def _safe_path(repo_dir: Path, rel_path: str) -> Path:
    root = repo_dir.resolve()
    target = (repo_dir / rel_path).resolve()
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise ToolError("path escapes repository root") from exc
    return target


def _clip(text: str) -> str:
    if len(text) <= MAX_TOOL_CHARS:
        return text
    return text[:MAX_TOOL_CHARS] + "\n...[TRUNCATED]..."


def list_directory_limited(
    repo_dir: Path,
    path: str = ".",
    depth: int = 2,
) -> str:
    if depth < 0 or depth > 2:
        raise ToolError("depth must be between 0 and 2")

    base = _safe_path(repo_dir, path)
    if not base.exists():
        raise ToolError(f"path does not exist: {path}")
    if not base.is_dir():
        raise ToolError(f"path is not a directory: {path}")

    base_depth = len(base.parts)
    entries: list[str] = []

    for item in sorted(base.rglob("*")):
        relative_depth = len(item.parts) - base_depth
        if relative_depth > depth:
            continue
        rel = item.relative_to(repo_dir).as_posix()
        entries.append(rel + ("/" if item.is_dir() else ""))

    return _clip("\n".join(entries))


def read_code_chunk(
    repo_dir: Path,
    file_path: str,
    target_line: int = 1,
    window: int = 40,
) -> str:
    if window < 1 or window > 80:
        raise ToolError("window must be between 1 and 80")

    path = _safe_path(repo_dir, file_path)
    if not path.is_file():
        raise ToolError(f"file does not exist: {file_path}")
    if path.suffix.lower() not in ALLOWED_TEXT_SUFFIXES:
        raise ToolError("unsupported file type")

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines:
        return ""

    target_line = max(1, min(target_line, len(lines)))
    half = window // 2
    start = max(1, target_line - half)
    end = min(len(lines), start + window - 1)

    rendered = [
        f"{line_no:04d}: {lines[line_no - 1]}"
        for line_no in range(start, end + 1)
    ]
    return _clip("\n".join(rendered))


def search_text(
    repo_dir: Path,
    query: str,
    max_results: int = 10,
) -> str:
    if not query:
        raise ToolError("query must be non-empty")
    if max_results < 1 or max_results > 10:
        raise ToolError("max_results must be between 1 and 10")

    matches: list[str] = []
    needle = query.lower()

    for path in sorted(repo_dir.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in ALLOWED_TEXT_SUFFIXES:
            continue

        rel = path.relative_to(repo_dir).as_posix()
        for line_no, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(),
            start=1,
        ):
            if needle in line.lower():
                matches.append(f"{rel}:{line_no}: {line.strip()}")
                if len(matches) >= max_results:
                    return _clip("\n".join(matches))

    return _clip("\n".join(matches) if matches else "NO_MATCHES")


def search_symbol(
    repo_dir: Path,
    symbol: str,
    max_results: int = 10,
) -> str:
    if not symbol:
        raise ToolError("symbol must be non-empty")

    escaped = re.escape(symbol)
    pattern = re.compile(
        rf"^\s*(?:def|class)\s+{escaped}\b|^\s*{escaped}\s*="
    )

    matches: list[str] = []
    for path in sorted(repo_dir.rglob("*.py")):
        rel = path.relative_to(repo_dir).as_posix()
        for line_no, line in enumerate(
            path.read_text(encoding="utf-8", errors="replace").splitlines(),
            start=1,
        ):
            if pattern.search(line):
                matches.append(f"{rel}:{line_no}: {line.strip()}")
                if len(matches) >= max_results:
                    return _clip("\n".join(matches))

    return _clip("\n".join(matches) if matches else "NO_MATCHES")


def get_test_definition(
    repo_dir: Path,
    test_target: str,
) -> str:
    file_part, _, function_name = test_target.partition("::")
    path = _safe_path(repo_dir, file_part)

    if not path.is_file():
        raise ToolError(f"test file does not exist: {file_part}")

    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not function_name:
        return _clip(
            "\n".join(f"{i:04d}: {line}" for i, line in enumerate(lines, 1))
        )

    start = None
    pattern = re.compile(rf"^\s*def\s+{re.escape(function_name)}\s*\(")

    for i, line in enumerate(lines):
        if pattern.search(line):
            start = i
            break

    if start is None:
        raise ToolError(f"test function not found: {function_name}")

    end = len(lines)
    for i in range(start + 1, len(lines)):
        if re.match(r"^def\s+\w+\s*\(", lines[i]):
            end = i
            break

    rendered = [
        f"{i + 1:04d}: {lines[i]}"
        for i in range(start, end)
    ]
    return _clip("\n".join(rendered))


def read_config(repo_dir: Path, file_path: str) -> str:
    path = _safe_path(repo_dir, file_path)
    if not path.is_file():
        raise ToolError(f"config does not exist: {file_path}")
    if path.suffix.lower() not in CONFIG_SUFFIXES:
        raise ToolError("read_config only accepts config file types")

    return _clip(path.read_text(encoding="utf-8", errors="replace"))
