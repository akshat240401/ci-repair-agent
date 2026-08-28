import pytest
from pydantic import ValidationError

from src.schemas.patch_plan import PatchPlan


def test_patch_plan_accepts_multi_file_edits():
    plan = PatchPlan.model_validate({
        "root_cause": "contract drift",
        "confidence": 0.95,
        "edits": [
            {
                "file": "src/a.py",
                "search": "old_a",
                "replace": "new_a",
                "reason": "producer",
            },
            {
                "file": "src/b.py",
                "search": "old_b",
                "replace": "new_b",
                "reason": "consumer",
            },
        ],
    })
    assert len(plan.edits) == 2


def test_patch_plan_rejects_empty_edit_list():
    with pytest.raises(ValidationError):
        PatchPlan.model_validate({
            "root_cause": "x",
            "confidence": 0.5,
            "edits": [],
        })
