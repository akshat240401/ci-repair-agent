from evaluation.evaluator import inspect_benchmark


def test_all_benchmark_targeted_failures_reproduce():
    summary = inspect_benchmark()
    assert summary.total_cases == 12
    assert summary.targeted_failures_reproduced == 12
    assert summary.full_suites_with_failure == 12
    assert summary.all_targeted_failures_reproduced is True
