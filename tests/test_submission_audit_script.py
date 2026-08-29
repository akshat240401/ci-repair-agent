from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_submission_audit_script_has_required_gates():
    text = (ROOT / "scripts" / "submission_audit.py").read_text(encoding="utf-8")

    required = [
        "check_secret_leakage",
        "check_ground_truth_isolation",
        "check_smoke_isolation",
        "check_no_code_wiring",
        "check_canonical_results",
        "check_evidence_consistency",
        "check_docs",
        "check_trajectories",
        "evaluation.evaluator",
        "evaluation.evidence_report",
        "evaluation.submission_cost_report",
        "evaluation.export_trajectories",
        "pytest",
    ]

    for item in required:
        assert item in text
