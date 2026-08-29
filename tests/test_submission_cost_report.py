from evaluation.submission_cost_report import _load_fair_baseline_runs


def test_cost_report_uses_only_twenty_case_quality_gate_runs():
    runs = _load_fair_baseline_runs(expected_cases=20)
    assert len(runs) == 3
    assert all(run["cases"] == 20 for run in runs)
    assert all("quality_gate" in run["file"] and "baseline" in run["file"] for run in runs)
