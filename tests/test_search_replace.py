from pathlib import Path

import pytest

from src.patching.search_replace import PatchApplicationError, apply_search_replace


def test_exact_unique_search_replace(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    file = repo / "example.py"
    file.write_text("x = 1\n", encoding="utf-8")

    result = apply_search_replace(
        repo,
        file="example.py",
        search="x = 1",
        replace="x = 2",
    )

    assert result.applied is True
    assert file.read_text(encoding="utf-8") == "x = 2\n"


def test_rejects_missing_search(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "example.py").write_text("x = 1\n", encoding="utf-8")

    with pytest.raises(PatchApplicationError, match="SEARCH_BLOCK_NOT_FOUND"):
        apply_search_replace(
            repo,
            file="example.py",
            search="x = 9",
            replace="x = 2",
        )


def test_rejects_ambiguous_search(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "example.py").write_text("x = 1\nx = 1\n", encoding="utf-8")

    with pytest.raises(PatchApplicationError, match="AMBIGUOUS_SEARCH_BLOCK"):
        apply_search_replace(
            repo,
            file="example.py",
            search="x = 1",
            replace="x = 2",
        )
