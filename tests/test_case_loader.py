from evaluation.case_loader import get_case, load_cases
def test_loads_all_five_starter_cases():
    cases=load_cases(); assert len(cases)==5; assert [c.case_id for c in cases]==["case_001","case_002","case_003","case_004","case_005"]
def test_get_challenging_case():
    case=get_case("case_003"); assert case.metadata.challenging is True; assert case.metadata.python_version=="3.11"
