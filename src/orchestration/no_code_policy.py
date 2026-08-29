from __future__ import annotations

from dataclasses import dataclass
from src.schemas.triage import TriageResult


@dataclass(frozen=True)
class NoCodePatchDecision:
    status: str
    reason: str


def evaluate_no_code_patch(triage: TriageResult) -> NoCodePatchDecision | None:
    """Narrow deterministic bypass for config/environment failures with no repo targets."""
    if triage.failure_type != "ENVIRONMENT_CONFIG":
        return None
    if triage.target_files:
        return None

    return NoCodePatchDecision(
        status="NO_CODE_PATCH_REQUIRED",
        reason=(
            "Triage classified the failure as ENVIRONMENT_CONFIG and identified "
            "no repository files requiring modification."
        ),
    )
