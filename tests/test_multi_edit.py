from pathlib import Path

import pytest

from src.patching.multi_edit import MultiEditError, apply_patch_plan
from src.schemas.patch_plan import PatchPlan


def test_applies_multiple_edits_across_files(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    a = repo / "a.py"
    b = repo / "b.py"

    a.write_text("NAME = 'old'\n", encoding="utf-8")
    b.write_text("VALUE = 'old'\n", encoding="utf-8")

    plan = PatchPlan.model_validate({
        "root_cause": "contract migration",
        "confidence": 0.9,
        "edits": [
            {
                "file": "a.py",
                "search": "NAME = 'old'",
                "replace": "NAME = 'new'",
                "reason": "update producer",
            },
            {
                "file": "b.py",
                "search": "VALUE = 'old'",
                "replace": "VALUE = 'new'",
                "reason": "update consumer",
            },
        ],
    })

    result = apply_patch_plan(repo, plan)

    assert result.files_modified == 2
    assert result.edits_applied == 2
    assert "new" in a.read_text(encoding="utf-8")
    assert "new" in b.read_text(encoding="utf-8")


def test_validation_is_transactional(tmp_path: Path):
    repo = tmp_path / "repo"
    repo.mkdir()

    a = repo / "a.py"
    b = repo / "b.py"
    a.write_text("A = 1\n", encoding="utf-8")
    b.write_text("B = 1\n", encoding="utf-8")

    plan = PatchPlan.model_validate({
        "root_cause": "test",
        "confidence": 0.9,
        "edits": [
            {
                "file": "a.py",
                "search": "A = 1",
                "replace": "A = 2",
                "reason": "first",
            },
            {
                "file": "b.py",
                "search": "DOES_NOT_EXIST",
                "replace": "B = 2",
                "reason": "invalid second edit",
            },
        ],
    })

    with pytest.raises(MultiEditError, match="SEARCH_BLOCK_NOT_FOUND"):
        apply_patch_plan(repo, plan)

    assert a.read_text(encoding="utf-8") == "A = 1\n"
    assert b.read_text(encoding="utf-8") == "B = 1\n"
