from evaluation.case_loader import get_case, load_cases
EXPECTED_CASE_IDS = [f"case_{i:03d}" for i in range(1, 21)]

def test_loads_all_benchmark_cases():
    cases=load_cases()
    assert len(cases)==20
    assert [c.case_id for c in cases]==EXPECTED_CASE_IDS

def test_get_challenging_case():
    case=get_case("case_003")
    assert case.metadata.challenging is True
    assert case.metadata.python_version=="3.11"

def test_hard_expansion_contains_multi_file_cases():
    for cid in ("case_013","case_015","case_019","case_020"):
        assert get_case(cid).metadata.challenging is True
