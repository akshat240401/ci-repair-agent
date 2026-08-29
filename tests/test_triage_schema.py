import pytest
from pydantic import ValidationError

from src.schemas.triage import TriageResult


def test_valid_triage_result():
    result = TriageResult(
        failure_type="LOGIC_BUG",
        confidence=0.9,
        evidence=["AssertionError in test"],
        target_files=["src/example.py"],
        suspected_root_cause="off-by-one",
        next_step="inspect pagination logic",
    )
    assert result.failure_type == "LOGIC_BUG"


def test_invalid_failure_type_rejected():
    with pytest.raises(ValidationError):
        TriageResult(
            failure_type="MAGIC",
            confidence=0.5,
            evidence=["x"],
            target_files=[],
            suspected_root_cause="unknown",
            next_step="inspect",
        )
