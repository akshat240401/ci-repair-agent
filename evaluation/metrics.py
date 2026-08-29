from __future__ import annotations
from evaluation.result_schema import RepairCaseResult
def verified_repair_rate(results:list[RepairCaseResult])->float:
    if not results: return 0.0
    verified=sum(1 for r in results if r.final_status=="VERIFIED_REPAIR" and r.patch_applied and r.syntax_passed and r.targeted_test_passed and r.full_suite_passed)
    return verified/len(results)
def average_latency_seconds(results:list[RepairCaseResult])->float:
    return 0.0 if not results else sum(r.latency_seconds for r in results)/len(results)
def average_cost_usd(results:list[RepairCaseResult])->float:
    return 0.0 if not results else sum(r.estimated_cost_usd for r in results)/len(results)
def unresolved_rate(results:list[RepairCaseResult])->float:
    return 0.0 if not results else sum(1 for r in results if r.final_status=="UNRESOLVED")/len(results)
