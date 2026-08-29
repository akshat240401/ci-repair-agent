from evaluation.evaluator import inspect_benchmark
def test_all_benchmark_targeted_failures_reproduce():
    s=inspect_benchmark()
    assert s.total_cases==20
    assert s.targeted_failures_reproduced==20
    assert s.full_suites_with_failure==20
    assert s.all_targeted_failures_reproduced is True
