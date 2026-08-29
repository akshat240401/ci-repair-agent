from evaluation.metrics import average_cost_usd, average_latency_seconds, unresolved_rate, verified_repair_rate
from evaluation.result_schema import RepairCaseResult
def mk(status:str,verified:bool=False,latency:float=0.0,cost:float=0.0)->RepairCaseResult:
    return RepairCaseResult(case_id="case_001",mode="baseline",final_status=status,patch_applied=verified,syntax_passed=verified,targeted_test_passed=verified,full_suite_passed=verified,latency_seconds=latency,estimated_cost_usd=cost)
def test_verified_repair_rate_requires_all_verification_gates():
    assert verified_repair_rate([mk("VERIFIED_REPAIR",True),mk("UNRESOLVED")])==0.5
def test_summary_metrics():
    results=[mk("VERIFIED_REPAIR",True,2.0,0.02),mk("UNRESOLVED",False,4.0,0.04)]
    assert average_latency_seconds(results)==3.0; assert average_cost_usd(results)==0.03; assert unresolved_rate(results)==0.5
