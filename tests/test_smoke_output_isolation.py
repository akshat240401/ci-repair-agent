from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_evaluate_smoke_uses_separate_output_directory():
    text = (ROOT / "evaluate.py").read_text(encoding="utf-8")
    assert '"results/smoke/repair_loop"' in text


def test_repair_loop_supports_custom_output_directory():
    text = (ROOT / "evaluation" / "repair_loop_experiment.py").read_text(encoding="utf-8")
    assert '"--output-dir"' in text
    assert "output_dir / \"results.json\"" in text
    assert "output_dir / \"summary.json\"" in text


def test_no_code_policy_is_wired_into_real_runner():
    text = (ROOT / "evaluation" / "repair_loop_experiment.py").read_text(encoding="utf-8")
    assert "evaluate_no_code_patch(triage)" in text
    assert "build_no_code_result(" in text
    assert '"NO_CODE_PATCH_REQUIRED"' in text


def test_clean_room_reads_smoke_summary():
    text = (ROOT / "scripts" / "clean_room_check.ps1").read_text(encoding="utf-8")
    assert r"results\smoke\repair_loop\summary.json" in text
