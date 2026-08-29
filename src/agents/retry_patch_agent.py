from __future__ import annotations
import json, os
from pathlib import Path
from openai import OpenAI
from pydantic import ValidationError
from baseline.context_builder import build_repository_context
from evaluation.case_loader import BenchmarkCase
from src.schemas.investigation import InvestigationResult
from src.schemas.patch_plan import PatchPlan
from src.schemas.triage import TriageResult

PROMPT_PATH = Path(__file__).with_name("retry_prompt.txt")

def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(text)
    return obj

def propose_retry_patch(
    case: BenchmarkCase,
    triage: TriageResult,
    investigation: InvestigationResult,
    previous_plan: PatchPlan,
    verification_feedback: dict,
) -> tuple[PatchPlan, dict]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    model = os.environ.get("MODEL_NAME", "gpt-5.6-luna")
    effort = os.environ.get("MODEL_REASONING_EFFORT", "low")

    user_input = (
        "===== TRIAGE =====\n" + json.dumps(triage.model_dump(), indent=2) +
        "\n===== INVESTIGATION =====\n" + json.dumps(investigation.model_dump(), indent=2) +
        "\n===== PREVIOUS PATCH =====\n" + json.dumps(previous_plan.model_dump(), indent=2) +
        "\n===== VERIFICATION FEEDBACK =====\n" + json.dumps(verification_feedback, indent=2) +
        "\n===== REPOSITORY =====\n" + build_repository_context(case)
    )

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        instructions=PROMPT_PATH.read_text(encoding="utf-8"),
        input=user_input,
        reasoning={"effort": effort},
    )
    try:
        plan = PatchPlan.model_validate(_extract_json(response.output_text))
    except (json.JSONDecodeError, ValidationError) as exc:
        raise RuntimeError(f"Retry patch agent returned invalid JSON: {exc}") from exc

    usage = getattr(response, "usage", None)
    return plan, {
        "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
        "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
    }
