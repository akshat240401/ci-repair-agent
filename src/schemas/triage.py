from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


FailureType = Literal[
    "SYNTAX_ERROR",
    "TYPE_ERROR",
    "LOGIC_BUG",
    "TEST_FAILURE",
    "DEPENDENCY_ERROR",
    "ENVIRONMENT_CONFIG",
    "NETWORK_TIMEOUT",
    "BUILD_ERROR",
    "RESOURCE_FAILURE",
    "UNKNOWN",
]


class TriageResult(BaseModel):
    failure_type: FailureType
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[str] = Field(min_length=1, max_length=5)
    target_files: list[str] = Field(default_factory=list, max_length=5)
    suspected_root_cause: str
    next_step: str
