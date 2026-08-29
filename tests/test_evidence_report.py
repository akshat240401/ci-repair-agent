from evaluation.evidence_report import HARD_CASES


def test_hard_case_set_is_explicit_and_stable():
    assert HARD_CASES == [
        "case_003",
        "case_010",
        "case_013",
        "case_015",
        "case_020",
    ]
