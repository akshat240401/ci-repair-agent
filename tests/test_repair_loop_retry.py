from pathlib import Path
from types import SimpleNamespace

import evaluation.repair_loop_experiment as repair_loop
from src.schemas.investigation import InvestigationResult
from src.schemas.patch_plan import PatchPlan
from src.schemas.triage import TriageResult


def test_retry_loop_recovers_on_second_attempt(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "tests").mkdir()

    (repo / "src" / "__init__.py").write_text("", encoding="utf-8")
    (repo / "src" / "calc.py").write_text(
        "def add(a, b):\n    return a - b\n",
        encoding="utf-8",
    )
    (repo / "tests" / "test_calc.py").write_text(
        "from src.calc import add\n\n"
        "def test_add():\n"
        "    assert add(2, 3) == 5\n",
        encoding="utf-8",
    )

    case = SimpleNamespace(
        case_id="case_retry",
        repo_dir=repo,
        metadata=SimpleNamespace(
            targeted_test="tests/test_calc.py::test_add"
        ),
    )

    triage = TriageResult(
        failure_type="LOGIC_BUG",
        confidence=0.99,
        evidence=["assert add(2, 3) == 5 failed"],
        target_files=["src/calc.py"],
        suspected_root_cause="wrong arithmetic operator",
        next_step="inspect add implementation",
    )

    investigation = InvestigationResult(
        root_cause="add uses subtraction instead of addition",
        evidence=["src/calc.py returns a - b"],
        target_files=["src/calc.py"],
        recommended_change_scope="single_file",
        confidence=0.99,
    )

    bad_plan = PatchPlan.model_validate({
        "root_cause": "incorrect first repair",
        "confidence": 0.7,
        "edits": [{
            "file": "src/calc.py",
            "search": "return a - b",
            "replace": "return a * b",
            "reason": "intentionally wrong first attempt",
        }],
    })

    good_plan = PatchPlan.model_validate({
        "root_cause": "correct arithmetic operator",
        "confidence": 0.99,
        "edits": [{
            "file": "src/calc.py",
            "search": "return a - b",
            "replace": "return a + b",
            "reason": "restore addition",
        }],
    })

    monkeypatch.setattr(
        repair_loop, "run_triage",
        lambda case: (triage, {"input_tokens": 0, "output_tokens": 0}),
    )
    monkeypatch.setattr(
        repair_loop, "run_investigation",
        lambda case, triage: (
            investigation,
            {"input_tokens": 0, "output_tokens": 0},
            [],
        ),
    )
    monkeypatch.setattr(
        repair_loop, "propose_patch_plan",
        lambda case, triage, investigation: (
            bad_plan,
            {"input_tokens": 0, "output_tokens": 0},
        ),
    )

    retry_calls = {"count": 0}

    def retry_agent(case, triage, investigation, previous_plan, verification_feedback):
        retry_calls["count"] += 1
        assert verification_feedback["targeted_test_passed"] is False
        return good_plan, {"input_tokens": 0, "output_tokens": 0}

    monkeypatch.setattr(repair_loop, "propose_retry_patch", retry_agent)

    result, diagnostics = repair_loop.run_case(case)

    assert result.final_status == "VERIFIED_REPAIR"
    assert result.attempts == 2
    assert retry_calls["count"] == 1
    assert diagnostics["stopped_reason"] == "VERIFIED_REPAIR"
    assert len(diagnostics["attempts"]) == 2
    assert diagnostics["attempts"][0]["verification"]["targeted_test_passed"] is False
    assert diagnostics["attempts"][1]["verification"]["full_suite_passed"] is True
