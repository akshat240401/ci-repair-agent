from __future__ import annotations
import argparse, json, shutil, tempfile, time
from pathlib import Path

from evaluation.case_loader import load_cases
from evaluation.metrics import verified_repair_rate
from evaluation.result_schema import RepairCaseResult
from src.agents.triage_agent import run_triage
from src.agents.investigation_agent import run_investigation
from src.agents.patch_agent import propose_patch_plan
from src.agents.retry_patch_agent import propose_retry_patch
from src.patching.multi_edit import MultiEditError, apply_patch_plan
from src.patching.fingerprint import patch_plan_hash
from src.state.hashing import repo_state_hash
from src.state.failure_signature import failure_signature
from src.state.loop_detector import LoopDetector
from src.verification.verifier import verify_patch
from src.orchestration.no_code_policy import evaluate_no_code_patch
from src.orchestration.no_code_result import build_no_code_result

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results" / "experiments" / "repair_loop"
MAX_ATTEMPTS = 3
INPUT_PRICE_PER_MILLION = 0.20
OUTPUT_PRICE_PER_MILLION = 1.20

def estimate_cost(i, o):
    return i / 1_000_000 * INPUT_PRICE_PER_MILLION + o / 1_000_000 * OUTPUT_PRICE_PER_MILLION

def feedback(v):
    return {
        "syntax_passed": v.syntax_passed,
        "targeted_test_passed": v.targeted_test_passed,
        "full_suite_passed": v.full_suite_passed,
        "syntax_stdout": v.syntax.stdout,
        "syntax_stderr": v.syntax.stderr,
        "targeted_stdout": v.targeted.stdout if v.targeted else "",
        "targeted_stderr": v.targeted.stderr if v.targeted else "",
        "full_suite_stdout": v.full_suite.stdout if v.full_suite else "",
        "full_suite_stderr": v.full_suite.stderr if v.full_suite else "",
    }

def run_case(case):
    started = time.perf_counter()
    triage, tu = run_triage(case)
    no_code = evaluate_no_code_patch(triage)
    if no_code is not None:
        total_in = tu["input_tokens"]
        total_out = tu["output_tokens"]
        result = build_no_code_result(
            case_id=case.case_id,
            decision=no_code,
            started=started,
            input_tokens=total_in,
            output_tokens=total_out,
            estimated_cost_usd=estimate_cost(total_in, total_out),
        )
        diagnostics = {
            "case_id": case.case_id,
            "attempts": [],
            "stopped_reason": "NO_CODE_PATCH_REQUIRED",
            "no_code_patch": {
                "reason": no_code.reason,
                "triage": triage.model_dump(),
            },
        }
        return result, diagnostics
    investigation, iu, trajectory = run_investigation(case, triage)
    plan, pu = propose_patch_plan(case, triage, investigation)

    total_in = tu["input_tokens"] + iu["input_tokens"] + pu["input_tokens"]
    total_out = tu["output_tokens"] + iu["output_tokens"] + pu["output_tokens"]

    diagnostics = {"case_id": case.case_id, "attempts": [], "stopped_reason": None}
    final = dict(patch=False, syntax=False, targeted=False, full=False, files=0, attempts=0)

    with tempfile.TemporaryDirectory(prefix=f"{case.case_id}_loop_") as temp:
        work_repo = Path(temp) / "repo"
        shutil.copytree(case.repo_dir, work_repo)
        detector = LoopDetector()
        detector.record_repo_state(repo_state_hash(work_repo))
        current_plan = plan

        for attempt in range(1, MAX_ATTEMPTS + 1):
            final["attempts"] = attempt
            p_hash = patch_plan_hash(current_plan)

            if detector.record_patch(p_hash):
                diagnostics["stopped_reason"] = "DUPLICATE_PATCH"
                break

            snapshot = Path(temp) / f"snapshot_{attempt}"
            shutil.copytree(work_repo, snapshot)

            record = {"attempt": attempt, "patch_hash": p_hash, "patch_plan": current_plan.model_dump()}

            try:
                applied = apply_patch_plan(work_repo, current_plan)
                final["patch"] = True
                final["files"] = applied.files_modified
            except MultiEditError as exc:
                record["patch_error"] = str(exc)
                diagnostics["attempts"].append(record)
                if attempt == MAX_ATTEMPTS:
                    diagnostics["stopped_reason"] = "MAX_ATTEMPTS"
                    break
                shutil.rmtree(work_repo)
                shutil.copytree(snapshot, work_repo)
                current_plan, ru = propose_retry_patch(
                    case, triage, investigation, current_plan,
                    {"patch_application_error": str(exc)}
                )
                total_in += ru["input_tokens"]; total_out += ru["output_tokens"]
                continue

            v = verify_patch(work_repo, case.metadata.targeted_test)
            final["syntax"] = v.syntax_passed
            final["targeted"] = v.targeted_test_passed
            final["full"] = v.full_suite_passed
            record["verification"] = feedback(v)

            if v.verified:
                diagnostics["attempts"].append(record)
                diagnostics["stopped_reason"] = "VERIFIED_REPAIR"
                break

            repo_hash = repo_state_hash(work_repo)
            sig = failure_signature(v.full_suite or v.targeted or v.syntax)
            record["repo_state_hash"] = repo_hash
            record["failure_signature"] = sig
            diagnostics["attempts"].append(record)

            if detector.record_repo_state(repo_hash):
                diagnostics["stopped_reason"] = "REPEATED_REPO_STATE"
                break
            repeated_failure = detector.record_failure(sig)
            if detector.has_two_state_oscillation():
                diagnostics["stopped_reason"] = "OSCILLATION"
                break
            if repeated_failure:
                diagnostics["stopped_reason"] = "NO_PROGRESS"
                break
            if attempt == MAX_ATTEMPTS:
                diagnostics["stopped_reason"] = "MAX_ATTEMPTS"
                break

            fb = feedback(v)
            shutil.rmtree(work_repo)
            shutil.copytree(snapshot, work_repo)
            current_plan, ru = propose_retry_patch(case, triage, investigation, current_plan, fb)
            total_in += ru["input_tokens"]; total_out += ru["output_tokens"]

    verified = final["patch"] and final["syntax"] and final["targeted"] and final["full"]
    result = RepairCaseResult(
        case_id=case.case_id,
        mode="advanced",
        final_status="VERIFIED_REPAIR" if verified else "UNRESOLVED",
        patch_applied=final["patch"],
        syntax_passed=final["syntax"],
        targeted_test_passed=final["targeted"],
        full_suite_passed=final["full"],
        attempts=final["attempts"],
        latency_seconds=time.perf_counter() - started,
        input_tokens=total_in,
        output_tokens=total_out,
        estimated_cost_usd=estimate_cost(total_in, total_out),
        files_modified=final["files"],
    )
    return result, diagnostics

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", default=None)
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    cases = load_cases()
    if args.case:
        cases = [c for c in cases if c.case_id == args.case]
        if not cases:
            raise SystemExit(f"Unknown case: {args.case}")

    output_dir = Path(args.output_dir) if args.output_dir else RESULTS_DIR
    if not output_dir.is_absolute():
        output_dir = PROJECT_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    results, diagnostics = [], []

    for case in cases:
        print(f"Running repair-loop experiment: {case.case_id} ...")
        r, d = run_case(case)
        results.append(r); diagnostics.append(d)
        print(f"  -> {r.final_status} | attempts={r.attempts} | stop={d['stopped_reason']}")

    (output_dir / "results.json").write_text(
        json.dumps([r.model_dump() for r in results], indent=2), encoding="utf-8"
    )
    (output_dir / "diagnostics.json").write_text(
        json.dumps(diagnostics, indent=2), encoding="utf-8"
    )

    summary = {
        "experiment": "verified_repair_loop",
        "cases": len(results),
        "verified_repairs": sum(r.final_status == "VERIFIED_REPAIR" for r in results),
        "verified_repair_rate": verified_repair_rate(results),
        "mean_attempts": sum(r.attempts for r in results) / len(results),
        "retry_cases": [r.case_id for r in results if r.attempts > 1],
        "unresolved_cases": [r.case_id for r in results if r.final_status != "VERIFIED_REPAIR"],
        "estimated_total_cost_usd": sum(r.estimated_cost_usd for r in results),
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("=" * 60)
    print("VERIFIED REPAIR LOOP EXPERIMENT")
    print("=" * 60)
    print(f"Verified Repair Rate:   {summary['verified_repair_rate'] * 100:.1f}%")
    print(f"Mean attempts:          {summary['mean_attempts']:.2f}")
    print(f"Retry cases:            {summary['retry_cases']}")
    print(f"Unresolved:             {summary['unresolved_cases']}")
    print(f"Estimated API cost:     ${summary['estimated_total_cost_usd']:.4f}")
    print("=" * 60)

if __name__ == "__main__":
    main()
