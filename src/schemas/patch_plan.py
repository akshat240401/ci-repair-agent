from __future__ import annotations

from pydantic import BaseModel, Field


class SearchReplaceEdit(BaseModel):
    file: str
    search: str = Field(min_length=1)
    replace: str
    reason: str


class PatchPlan(BaseModel):
    root_cause: str
    edits: list[SearchReplaceEdit] = Field(min_length=1, max_length=6)
    confidence: float = Field(ge=0.0, le=1.0)
