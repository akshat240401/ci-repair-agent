from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import tempfile
import time

from baseline.baseline_agent import propose_patch
from evaluation.case_loader import load_cases
from evaluation.metrics import verified_repair_rate
from evaluation.result_schema import RepairCaseResult
from src.agents.triage_agent import run_triage
from src.patching.search_replace import (
    PatchApplicationError,
    apply_search_replace,
)
from src.verification.verifier import verify_patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results" / "experiments" / "triage"

INPUT_PRICE_PER_MILLION = 0.20
OUTPUT_PRICE_PER_MILLION = 1.20


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens / 1_000_000 * INPUT_PRICE_PER_MILLION
        + output_tokens / 1_000_000 * OUTPUT_PRICE_PER_MILLION
    )


def run_case(case) -> tuple[RepairCaseResult, dict]:
    started = time.perf_counter()

    triage, triage_usage = run_triage(case)
    proposal, repair_usage = propose_patch(
        case,
        preprocess_failure_log=False,
        triage=triage,
    )

    total_input = triage_usage["input_tokens"] + repair_usage["input_tokens"]
    total_output = triage_usage["output_tokens"] + repair_usage["output_tokens"]

    diagnostics = {
        "case_id": case.case_id,
        "expected_failure_type": case.metadata.expected_failure_type,
        "triage": triage.model_dump(),
        "triage_type_correct": (
            triage.failure_type == case.metadata.expected_failure_type
        ),
        "proposal": proposal.model_dump(),
        "patch_error": None,
        "regression_stdout": "",
        "regression_stderr": "",
    }

    with tempfile.TemporaryDirectory(prefix=f"{case.case_id}_triage_") as temp:
        work_repo = Path(temp) / "repo"
        shutil.copytree(case.repo_dir, work_repo)

        patch_applied = False
        syntax_passed = False
        targeted_passed = False
        full_passed = False

        try:
            apply_search_replace(
                work_repo,
                file=proposal.file,
                search=proposal.search,
                replace=proposal.replace,
            )
            patch_applied = True

            verification = verify_patch(
                work_repo,
                case.metadata.targeted_test,
            )
            syntax_passed = verification.syntax_passed
            targeted_passed = verification.targeted_test_passed
            full_passed = verification.full_suite_passed

            if verification.full_suite is not None:
                diagnostics["regression_stdout"] = verification.full_suite.stdout
                diagnostics["regression_stderr"] = verification.full_suite.stderr

        except PatchApplicationError as exc:
            diagnostics["patch_error"] = str(exc)

    verified = (
        patch_applied
        and syntax_passed
        and targeted_passed
        and full_passed
    )

    result = RepairCaseResult(
        case_id=case.case_id,
        mode="advanced",
        final_status="VERIFIED_REPAIR" if verified else "UNRESOLVED",
        patch_applied=patch_applied,
        syntax_passed=syntax_passed,
        targeted_test_passed=targeted_passed,
        full_suite_passed=full_passed,
        attempts=1,
        latency_seconds=time.perf_counter() - started,
        input_tokens=total_input,
        output_tokens=total_output,
        estimated_cost_usd=estimate_cost(total_input, total_output),
        files_modified=1 if patch_applied else 0,
    )

    return result, diagnostics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default=None)
    args = parser.parse_args()

    cases = load_cases()
    if args.case:
        cases = [case for case in cases if case.case_id == args.case]
        if not cases:
            raise SystemExit(f"Unknown case: {args.case}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    diagnostics = []

    for case in cases:
        print(f"Running triage experiment: {case.case_id} ...")
        result, diag = run_case(case)
        results.append(result)
        diagnostics.append(diag)
        print(
            f"  -> {result.final_status} | "
            f"triage={diag['triage']['failure_type']} "
            f"(expected {diag['expected_failure_type']})"
        )

    (RESULTS_DIR / "results.json").write_text(
        json.dumps([r.model_dump() for r in results], indent=2),
        encoding="utf-8",
    )
    (RESULTS_DIR / "diagnostics.json").write_text(
        json.dumps(diagnostics, indent=2),
        encoding="utf-8",
    )

    correct = sum(d["triage_type_correct"] for d in diagnostics)
    vrr = verified_repair_rate(results)

    summary = {
        "experiment": "triage_agent",
        "cases": len(results),
        "triage_type_correct": correct,
        "triage_accuracy": correct / len(results) if results else 0.0,
        "verified_repairs": sum(
            r.final_status == "VERIFIED_REPAIR" for r in results
        ),
        "verified_repair_rate": vrr,
        "unresolved_cases": [
            r.case_id for r in results
            if r.final_status != "VERIFIED_REPAIR"
        ],
        "total_input_tokens": sum(r.input_tokens for r in results),
        "total_output_tokens": sum(r.output_tokens for r in results),
        "estimated_total_cost_usd": sum(
            r.estimated_cost_usd for r in results
        ),
    }

    (RESULTS_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print("=" * 60)
    print("TRIAGE AGENT EXPERIMENT")
    print("=" * 60)
    print(
        f"Triage accuracy:        "
        f"{summary['triage_accuracy'] * 100:.1f}% "
        f"({correct}/{len(results)})"
    )
    print(
        f"Verified Repair Rate:   "
        f"{summary['verified_repair_rate'] * 100:.1f}%"
    )
    print(f"Unresolved:             {summary['unresolved_cases']}")
    print(f"Input tokens:           {summary['total_input_tokens']}")
    print(f"Output tokens:          {summary['total_output_tokens']}")
    print(
        f"Estimated API cost:     "
        f"${summary['estimated_total_cost_usd']:.4f}"
    )
    print(f"Summary: {RESULTS_DIR / 'summary.json'}")
    print("=" * 60)


if __name__ == "__main__":
    main()
