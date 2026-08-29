import time

from src.orchestration.no_code_policy import NoCodePatchDecision
from src.orchestration.no_code_result import build_no_code_result


def test_build_no_code_result():
    decision = NoCodePatchDecision(
        status="NO_CODE_PATCH_REQUIRED",
        reason="environment-only remediation",
    )

    result = build_no_code_result(
        case_id="case_config_only",
        decision=decision,
        started=time.perf_counter(),
    )

    assert result.final_status == "NO_CODE_PATCH_REQUIRED"
    assert result.patch_applied is False
    assert result.attempts == 0
    assert result.files_modified == 0
