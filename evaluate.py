from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def run_module(module: str, *args: str) -> None:
    command = [sys.executable, "-m", module, *args]
    print()
    print("$ " + " ".join(command))
    completed = subprocess.run(command, cwd=ROOT)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def require_api_key() -> None:
    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit(
            "OPENAI_API_KEY is required for API-backed evaluation.\n"
            "Set it in the shell, then rerun this command."
        )


def print_submission_summary() -> None:
    evidence_path = ROOT / "results" / "final_evidence" / "evidence_summary.json"
    cost_path = ROOT / "results" / "submission" / "cost_comparison.json"

    if not evidence_path.exists() or not cost_path.exists():
        return

    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    cost = json.loads(cost_path.read_text(encoding="utf-8"))

    print()
    print("=" * 68)
    print("ONE-COMMAND EVALUATION SUMMARY")
    print("=" * 68)
    print(
        f"Baseline mean VRR:   "
        f"{evidence['baseline_mean_vrr'] * 100:.1f}%"
    )
    print(
        f"Current final VRR:   "
        f"{evidence['final_vrr'] * 100:.1f}%"
    )
    print(
        f"Improvement:         "
        f"{evidence['absolute_improvement_pp']:.1f} pp"
    )
    print(
        f"Baseline mean cost:  "
        f"${cost['baseline']['mean_cost_usd']:.6f}"
    )
    print(
        f"Final current cost:  "
        f"${cost['final_current_dev_run']['estimated_cost_usd']:.6f}"
    )
    print("=" * 68)


def deterministic_evaluation() -> None:
    run_module("pytest", "-q", "tests")
    run_module("evaluation.evaluator", "--mode", "inspect")
    run_module("evaluation.evidence_report")
    run_module("evaluation.submission_cost_report")
    run_module("evaluation.export_trajectories")
    print_submission_summary()


def api_smoke(case_id: str) -> None:
    require_api_key()
    run_module("evaluation.repair_loop_experiment", "--case", case_id)


def full_agent_evaluation() -> None:
    require_api_key()
    run_module("evaluation.repair_loop_experiment")
    run_module("evaluation.evidence_report")
    run_module("evaluation.submission_cost_report")
    run_module("evaluation.export_trajectories")
    print_submission_summary()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Single entry point for CI repair agent evaluation."
    )
    parser.add_argument(
        "--mode",
        choices=["deterministic", "smoke", "full"],
        default="deterministic",
        help=(
            "deterministic: tests + benchmark validation + reports; "
            "smoke: one API-backed repair case; "
            "full: complete API-backed 20-case repair evaluation."
        ),
    )
    parser.add_argument(
        "--case",
        default="case_010",
        help="Benchmark case used by --mode smoke.",
    )
    args = parser.parse_args()

    if args.mode == "deterministic":
        deterministic_evaluation()
    elif args.mode == "smoke":
        api_smoke(args.case)
    else:
        full_agent_evaluation()


if __name__ == "__main__":
    main()
