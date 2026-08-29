from __future__ import annotations

import json
import os
from pathlib import Path

from openai import OpenAI
from pydantic import ValidationError

from evaluation.case_loader import BenchmarkCase
from src.preprocessing.log_preprocessor import preprocess_log
from src.schemas.triage import TriageResult


PROMPT_PATH = Path(__file__).with_name("triage_prompt.txt")


def build_triage_input(case: BenchmarkCase) -> str:
    failing_log = preprocess_log(
        case.log_path.read_text(encoding="utf-8", errors="replace")
    )

    manifest = [
        path.relative_to(case.repo_dir).as_posix()
        for path in sorted(case.repo_dir.rglob("*"))
        if path.is_file()
    ]

    return (
        "===== FAILING CI LOG =====\n"
        f"{failing_log}\n"
        "===== REPOSITORY MANIFEST =====\n"
        + "\n".join(manifest)
    )


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return json.loads(text)


def run_triage(case: BenchmarkCase) -> tuple[TriageResult, dict]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    model = os.environ.get("MODEL_NAME", "gpt-5.6-luna")
    effort = os.environ.get("MODEL_REASONING_EFFORT", "low")

    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model=model,
        instructions=PROMPT_PATH.read_text(encoding="utf-8"),
        input=build_triage_input(case),
        reasoning={"effort": effort},
    )

    try:
        triage = TriageResult.model_validate(_extract_json(response.output_text))
    except (json.JSONDecodeError, ValidationError) as exc:
        raise RuntimeError(
            f"Triage agent returned invalid JSON: {exc}\n"
            f"Raw output:\n{response.output_text}"
        ) from exc

    manifest = {
        path.relative_to(case.repo_dir).as_posix()
        for path in case.repo_dir.rglob("*")
        if path.is_file()
    }

    invented = [path for path in triage.target_files if path not in manifest]
    if invented:
        raise RuntimeError(
            f"Triage agent invented repository paths: {invented}"
        )

    usage = getattr(response, "usage", None)
    return triage, {
        "model": model,
        "input_tokens": int(getattr(usage, "input_tokens", 0) or 0),
        "output_tokens": int(getattr(usage, "output_tokens", 0) or 0),
    }
