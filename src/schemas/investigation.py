from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


ToolName = Literal[
    "read_code_chunk",
    "search_text",
    "search_symbol",
    "get_test_definition",
    "list_directory_limited",
    "read_config",
]


class ToolRequest(BaseModel):
    action: Literal["tool"]
    tool: ToolName
    arguments: dict
    reason: str


class InvestigationResult(BaseModel):
    action: Literal["final"] = "final"
    root_cause: str
    evidence: list[str] = Field(min_length=1, max_length=8)
    target_files: list[str] = Field(min_length=1, max_length=5)
    recommended_change_scope: Literal["single_file", "multi_file"]
    confidence: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="before")
    @classmethod
    def normalize_change_scope(cls, data: Any):
        """
        Canonicalize free-form model wording into one of two stored values.

        The model may say things like:
          - two_files
          - cross_file_contract
          - multiple modules
          - one-file

        We normalize recognizable wording first. If wording is novel or
        ambiguous, target_files is the source of truth:
          1 target file  -> single_file
          2+ target files -> multi_file

        This prevents harmless vocabulary variation from aborting a run while
        preserving a strict canonical schema downstream.
        """
        if not isinstance(data, dict):
            return data

        data = dict(data)
        raw_scope = data.get("recommended_change_scope")
        target_files = data.get("target_files") or []

        normalized = (
            str(raw_scope).strip().lower().replace("-", "_").replace(" ", "_")
            if raw_scope is not None
            else ""
        )

        multi_markers = (
            "multi",
            "multiple",
            "cross_file",
            "cross_module",
            "two_file",
            "two_files",
            "several_file",
            "several_files",
        )
        single_markers = (
            "single",
            "one_file",
            "one_files",
        )

        if any(marker in normalized for marker in multi_markers):
            data["recommended_change_scope"] = "multi_file"
        elif any(marker in normalized for marker in single_markers):
            data["recommended_change_scope"] = "single_file"
        elif len(target_files) >= 2:
            data["recommended_change_scope"] = "multi_file"
        else:
            data["recommended_change_scope"] = "single_file"

        return data
