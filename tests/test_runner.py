from evaluation.case_loader import get_case
from evaluation.runner import run_full_suite, run_targeted_test
def test_targeted_failure_is_reproduced():
    case=get_case("case_001"); result=run_targeted_test(case.repo_dir,case.metadata.targeted_test); assert result.status=="FAIL"; assert result.exit_code!=0
def test_full_suite_contains_failure():
    case=get_case("case_001"); result=run_full_suite(case.repo_dir); assert result.status=="FAIL"; assert result.exit_code!=0
