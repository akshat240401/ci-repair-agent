from __future__ import annotations

import json
import os
from pathlib import Path

from openai import OpenAI
from pydantic import ValidationError

from evaluation.case_loader import BenchmarkCase
from src.preprocessing.log_preprocessor import preprocess_log
from src.schemas.investigation import InvestigationResult, ToolRequest
from src.schemas.triage import TriageResult
from src.tools.executor import MAX_TOOL_CALLS, execute_tool


PROMPT_PATH = Path(__file__).with_name("investigation_prompt.txt")


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
        raise json.JSONDecodeError(
            "Expected a JSON object",
            text,
            0,
        )

    return obj


def _manifest(case: BenchmarkCase) -> list[str]:
    return [
        path.relative_to(case.repo_dir).as_posix()
        for path in sorted(case.repo_dir.rglob("*"))
        if path.is_file()
    ]


def _initial_input(case: BenchmarkCase, triage: TriageResult) -> str:
    log = preprocess_log(
        case.log_path.read_text(encoding="utf-8", errors="replace")
    )
    return (
        "===== FAILING CI LOG =====\n"
        f"{log}\n"
        "===== TRIAGE REPORT =====\n"
        f"{json.dumps(triage.model_dump(), indent=2)}\n"
        "===== REPOSITORY MANIFEST =====\n"
        + "\n".join(_manifest(case))
    )


def run_investigation(
    case: BenchmarkCase,
    triage: TriageResult,
) -> tuple[InvestigationResult, dict, list[dict]]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")

    model = os.environ.get("MODEL_NAME", "gpt-5.6-luna")
    effort = os.environ.get("MODEL_REASONING_EFFORT", "low")
    client = OpenAI(api_key=api_key)

    instructions = PROMPT_PATH.read_text(encoding="utf-8")
    conversation = _initial_input(case, triage)
    trajectory: list[dict] = []

    total_input_tokens = 0
    total_output_tokens = 0

    for turn in range(1, MAX_TOOL_CALLS + 2):
        response = client.responses.create(
            model=model,
            instructions=instructions,
            input=conversation,
            reasoning={"effort": effort},
        )

        usage = getattr(response, "usage", None)
        total_input_tokens += int(getattr(usage, "input_tokens", 0) or 0)
        total_output_tokens += int(getattr(usage, "output_tokens", 0) or 0)

        try:
            raw = _extract_json(response.output_text)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Investigation agent returned invalid JSON on turn {turn}: "
                f"{exc}\nRaw output:\n{response.output_text}"
            ) from exc

        action = raw.get("action")

        if action == "final":
            try:
                result = InvestigationResult.model_validate(raw)
            except ValidationError as exc:
                raise RuntimeError(
                    f"Invalid final investigation result: {exc}"
                ) from exc

            manifest = set(_manifest(case))
            invented = [f for f in result.target_files if f not in manifest]
            if invented:
                raise RuntimeError(
                    f"Investigation agent invented paths: {invented}"
                )

            trajectory.append({
                "turn": turn,
                "action": "final",
                "result": result.model_dump(),
            })
            return (
                result,
                {
                    "model": model,
                    "input_tokens": total_input_tokens,
                    "output_tokens": total_output_tokens,
                    "tool_calls": sum(
                        item["action"] == "tool" for item in trajectory
                    ),
                },
                trajectory,
            )

        try:
            request = ToolRequest.model_validate(raw)
        except ValidationError as exc:
            raise RuntimeError(
                f"Invalid tool request on turn {turn}: {exc}"
            ) from exc

        tool_calls_so_far = sum(
            item["action"] == "tool" for item in trajectory
        )
        if tool_calls_so_far >= MAX_TOOL_CALLS:
            raise RuntimeError("Investigation tool-call budget exhausted.")

        output = execute_tool(
            case.repo_dir,
            request.tool,
            request.arguments,
        )

        trajectory.append({
            "turn": turn,
            "action": "tool",
            "tool": request.tool,
            "arguments": request.arguments,
            "reason": request.reason,
            "output": output,
        })

        conversation += (
            "\n\n===== INVESTIGATION TURN =====\n"
            f"REQUEST:\n{json.dumps(request.model_dump(), indent=2)}\n"
            f"TOOL RESULT:\n{output}\n"
        )

    raise RuntimeError("Investigation ended without a final result.")
