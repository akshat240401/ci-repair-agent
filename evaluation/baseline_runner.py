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
from src.patching.search_replace import PatchApplicationError, apply_search_replace
from src.verification.verifier import verify_patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results" / "baseline"


INPUT_PRICE_PER_MILLION = 0.20
OUTPUT_PRICE_PER_MILLION = 1.20


def estimate_cost(input_tokens: int, output_tokens: int) -> float:
    return (
        input_tokens / 1_000_000 * INPUT_PRICE_PER_MILLION
        + output_tokens / 1_000_000 * OUTPUT_PRICE_PER_MILLION
    )


def run_case(case) -> RepairCaseResult:
    started = time.perf_counter()
    proposal, usage = propose_patch(case)

    input_tokens = usage["input_tokens"]
    output_tokens = usage["output_tokens"]

    with tempfile.TemporaryDirectory(prefix=f"{case.case_id}_baseline_") as temp:
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

        except PatchApplicationError:
            pass

    verified = (
        patch_applied
        and syntax_passed
        and targeted_passed
        and full_passed
    )

    return RepairCaseResult(
        case_id=case.case_id,
        mode="baseline",
        final_status="VERIFIED_REPAIR" if verified else "UNRESOLVED",
        patch_applied=patch_applied,
        syntax_passed=syntax_passed,
        targeted_test_passed=targeted_passed,
        full_suite_passed=full_passed,
        attempts=1,
        latency_seconds=time.perf_counter() - started,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=estimate_cost(input_tokens, output_tokens),
        files_modified=1 if patch_applied else 0,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default=None)
    args = parser.parse_args()

    cases = load_cases()
    if args.case:
        cases = [c for c in cases if c.case_id == args.case]
        if not cases:
            raise SystemExit(f"Unknown case: {args.case}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results: list[RepairCaseResult] = []
    for case in cases:
        print(f"Running baseline: {case.case_id} ...")
        result = run_case(case)
        results.append(result)
        print(f"  -> {result.final_status}")

    results_path = RESULTS_DIR / "results.json"
    results_path.write_text(
        json.dumps([r.model_dump() for r in results], indent=2),
        encoding="utf-8",
    )

    rate = verified_repair_rate(results)

    summary = {
        "cases": len(results),
        "verified_repairs": sum(
            1 for r in results if r.final_status == "VERIFIED_REPAIR"
        ),
        "verified_repair_rate": rate,
        "total_input_tokens": sum(r.input_tokens for r in results),
        "total_output_tokens": sum(r.output_tokens for r in results),
        "estimated_total_cost_usd": sum(r.estimated_cost_usd for r in results),
    }

    summary_path = RESULTS_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=" * 60)
    print("BASELINE RESULTS")
    print("=" * 60)
    print(f"Cases:                 {summary['cases']}")
    print(f"Verified repairs:      {summary['verified_repairs']}")
    print(f"Verified Repair Rate:  {rate * 100:.1f}%")
    print(f"Input tokens:          {summary['total_input_tokens']}")
    print(f"Output tokens:         {summary['total_output_tokens']}")
    print(f"Estimated API cost:    ${summary['estimated_total_cost_usd']:.4f}")
    print(f"Results: {results_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
