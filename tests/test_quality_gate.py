from evaluation.quality_gate import aggregate


def test_aggregate_computes_mean_and_range():
    runs = [
        {
            "run": 1,
            "verified_repair_rate": 0.75,
            "verified_repairs": 9,
            "estimated_cost_usd": 0.01,
            "unresolved_cases": ["case_010", "case_011", "case_012"],
        },
        {
            "run": 2,
            "verified_repair_rate": 1.0,
            "verified_repairs": 12,
            "estimated_cost_usd": 0.01,
            "unresolved_cases": [],
        },
    ]

    summary = aggregate("baseline", runs)

    assert summary["mean_vrr"] == 0.875
    assert summary["min_vrr"] == 0.75
    assert summary["max_vrr"] == 1.0
    assert summary["mean_verified_repairs"] == 10.5
