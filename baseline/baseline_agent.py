from __future__ import annotations

import json
import os
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

from baseline.context_builder import build_baseline_input
from evaluation.case_loader import BenchmarkCase


PROMPT_PATH = Path(__file__).with_name("prompt.txt")


class BaselinePatchProposal(BaseModel):
    root_cause: str
    file: str
    search: str
    replace: str
    confidence: float = Field(ge=0.0, le=1.0)


def _extract_json(text: str) -> dict:
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()
        if lines:
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    return json.loads(text)


def propose_patch(case: BenchmarkCase) -> tuple[BaselinePatchProposal, dict]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Set it in the current PowerShell session "
            "before running the baseline."
        )

    model = os.environ.get("MODEL_NAME", "gpt-5.6-luna")
    effort = os.environ.get("MODEL_REASONING_EFFORT", "low")

    client = OpenAI(api_key=api_key)
    instructions = PROMPT_PATH.read_text(encoding="utf-8")
    user_input = build_baseline_input(case)

    response = client.responses.create(
        model=model,
        instructions=instructions,
        input=user_input,
        reasoning={"effort": effort},
    )

    try:
        raw = _extract_json(response.output_text)
        proposal = BaselinePatchProposal.model_validate(raw)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise RuntimeError(
            f"Baseline model returned invalid patch JSON: {exc}\n"
            f"Raw output:\n{response.output_text}"
        ) from exc

    usage = getattr(response, "usage", None)
    usage_info = {
        "model": model,
        "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
        "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
    }

    return proposal, usage_info
