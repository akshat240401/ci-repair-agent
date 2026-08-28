from evaluation.case_loader import get_case, load_cases


EXPECTED_CASE_IDS = [f"case_{i:03d}" for i in range(1, 13)]


def test_loads_all_benchmark_cases():
    cases = load_cases()
    assert len(cases) == 12
    assert [case.case_id for case in cases] == EXPECTED_CASE_IDS


def test_get_challenging_case():
    case = get_case("case_003")
    assert case.metadata.challenging is True
    assert case.metadata.python_version == "3.11"
