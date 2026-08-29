from __future__ import annotations

import json
import os
from pathlib import Path

from openai import OpenAI
from pydantic import ValidationError

from baseline.context_builder import build_repository_context
from evaluation.case_loader import BenchmarkCase
from src.preprocessing.log_preprocessor import preprocess_log
from src.schemas.investigation import InvestigationResult
from src.schemas.patch_plan import PatchPlan
from src.schemas.triage import TriageResult


PROMPT_PATH = Path(__file__).with_name("patch_prompt.txt")


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(text)
    if not isinstance(obj, dict):
        raise json.JSONDecodeError("Expected JSON object", text, 0)
    return obj


def build_patch_input(
    case: BenchmarkCase,
    triage: TriageResult,
    investigation: InvestigationResult,
) -> str:
    failing_log = preprocess_log(
        case.log_path.read_text(encoding="utf-8", errors="replace")
    )

    return (
        "===== FAILING CI LOG =====\n"
        f"{failing_log}\n"
        "===== TRIAGE REPORT =====\n"
        f"{json.dumps(triage.model_dump(), indent=2)}\n"
        "===== INVESTIGATION REPORT =====\n"
        f"{json.dumps(investigation.model_dump(), indent=2)}\n"
        "===== REPOSITORY =====\n"
        f"{build_repository_context(case)}"
    )


def propose_patch_plan(
    case: BenchmarkCase,
    triage: TriageResult,
    investigation: InvestigationResult,
) -> tuple[PatchPlan, dict]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    model = os.environ.get("MODEL_NAME", "gpt-5.6-luna")
    effort = os.environ.get("MODEL_REASONING_EFFORT", "low")

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        instructions=PROMPT_PATH.read_text(encoding="utf-8"),
        input=build_patch_input(case, triage, investigation),
        reasoning={"effort": effort},
    )

    try:
        plan = PatchPlan.model_validate(_extract_json(response.output_text))
    except (json.JSONDecodeError, ValidationError) as exc:
        raise RuntimeError(
            f"Patch agent returned invalid JSON: {exc}\n"
            f"Raw output:\n{response.output_text}"
        ) from exc

    usage = getattr(response, "usage", None)
    return plan, {
        "model": model,
        "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
        "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
    }
