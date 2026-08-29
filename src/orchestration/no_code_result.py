from __future__ import annotations

import time

from evaluation.result_schema import RepairCaseResult
from src.orchestration.no_code_policy import NoCodePatchDecision


def build_no_code_result(
    case_id: str,
    decision: NoCodePatchDecision,
    started: float,
    input_tokens: int = 0,
    output_tokens: int = 0,
    estimated_cost_usd: float = 0.0,
) -> RepairCaseResult:
    return RepairCaseResult(
        case_id=case_id,
        mode="advanced",
        final_status=decision.status,
        patch_applied=False,
        syntax_passed=False,
        targeted_test_passed=False,
        full_suite_passed=False,
        attempts=0,
        latency_seconds=time.perf_counter() - started,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=estimated_cost_usd,
        files_modified=0,
    )
