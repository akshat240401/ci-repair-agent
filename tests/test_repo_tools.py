from pathlib import Path

import pytest

from src.tools.repo_tools import (
    ToolError,
    get_test_definition,
    list_directory_limited,
    read_code_chunk,
    search_symbol,
    search_text,
)


def _repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "src" / "example.py").write_text(
        "VALUE = 1\n\ndef add(a, b):\n    return a + b\n",
        encoding="utf-8",
    )
    (repo / "tests" / "test_example.py").write_text(
        "from src.example import add\n\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )
    return repo


def test_bounded_repo_tools(tmp_path):
    repo = _repo(tmp_path)

    assert "def add" in read_code_chunk(
        repo, "src/example.py", target_line=3, window=4
    )
    assert "src/example.py" in search_text(repo, "return a + b")
    assert "src/example.py" in search_symbol(repo, "add")
    assert "assert add(2, 3)" in get_test_definition(
        repo, "tests/test_example.py::test_add"
    )
    assert "src/example.py" in list_directory_limited(repo, ".", depth=2)


def test_path_escape_is_rejected(tmp_path):
    repo = _repo(tmp_path)
    outside = tmp_path / "secret.txt"
    outside.write_text("secret", encoding="utf-8")

    with pytest.raises(ToolError):
        read_code_chunk(repo, "../secret.txt")
