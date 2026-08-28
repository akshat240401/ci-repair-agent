from evaluation.evaluator import inspect_benchmark
def test_all_starter_targeted_failures_reproduce():
    summary=inspect_benchmark(); assert summary.total_cases==5; assert summary.targeted_failures_reproduced==5; assert summary.all_targeted_failures_reproduced is True
