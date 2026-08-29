from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field
RunKind = Literal["targeted", "full"]
RunStatus = Literal["PASS", "FAIL", "ERROR"]
class CommandResult(BaseModel):
    kind: RunKind
    command: list[str]
    exit_code: int | None
    status: RunStatus
    duration_seconds: float = Field(ge=0)
    stdout: str = ""
    stderr: str = ""
class CaseInspectionResult(BaseModel):
    case_id: str
    targeted: CommandResult
    full_suite: CommandResult
    targeted_failure_reproduced: bool
    full_suite_has_failure: bool
class BenchmarkInspectionSummary(BaseModel):
    total_cases: int
    targeted_failures_reproduced: int
    full_suites_with_failure: int
    all_targeted_failures_reproduced: bool
    cases: list[CaseInspectionResult]
class RepairCaseResult(BaseModel):
    case_id: str
    mode: Literal["baseline", "advanced"]
    final_status: Literal["VERIFIED_REPAIR", "NO_CODE_PATCH_REQUIRED", "UNRESOLVED"]
    patch_applied: bool = False
    syntax_passed: bool = False
    targeted_test_passed: bool = False
    full_suite_passed: bool = False
    attempts: int = Field(default=0, ge=0)
    latency_seconds: float = Field(default=0.0, ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    estimated_cost_usd: float = Field(default=0.0, ge=0)
    files_modified: int = Field(default=0, ge=0)
    lines_added: int = Field(default=0, ge=0)
    lines_removed: int = Field(default=0, ge=0)
