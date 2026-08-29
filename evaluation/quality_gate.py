from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean, pstdev

from evaluation.baseline_runner import run_case as run_baseline_case
from evaluation.case_loader import load_cases
from evaluation.metrics import verified_repair_rate
from evaluation.preprocessor_experiment import run_case as run_preprocessor_case


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_ROOT = PROJECT_ROOT / "results" / "quality_gate"


def _run_baseline_round(cases, run_index: int) -> dict:
    run_dir = RESULTS_ROOT / "baseline" / f"run_{run_index:02d}"
    run_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for case in cases:
        print(f"[baseline run {run_index}] {case.case_id}")
        result = run_baseline_case(case)
        results.append(result)

    (run_dir / "results.json").write_text(
        json.dumps([r.model_dump() for r in results], indent=2),
        encoding="utf-8",
    )

    summary = {
        "run": run_index,
        "cases": len(results),
        "verified_repairs": sum(r.final_status == "VERIFIED_REPAIR" for r in results),
        "verified_repair_rate": verified_repair_rate(results),
        "input_tokens": sum(r.input_tokens for r in results),
        "output_tokens": sum(r.output_tokens for r in results),
        "estimated_cost_usd": sum(r.estimated_cost_usd for r in results),
        "unresolved_cases": [
            r.case_id for r in results if r.final_status != "VERIFIED_REPAIR"
        ],
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    return summary


def _run_preprocessor_round(cases, run_index: int) -> dict:
    run_dir = RESULTS_ROOT / "preprocessor" / f"run_{run_index:02d}"
    run_dir.mkdir(parents=True, exist_ok=True)

    results = []
    diagnostics = []

    for case in cases:
        print(f"[preprocessor run {run_index}] {case.case_id}")
        result, diag = run_preprocessor_case(case)
        results.append(result)
        diagnostics.append(diag)

    (run_dir / "results.json").write_text(
        json.dumps([r.model_dump() for r in results], indent=2),
        encoding="utf-8",
    )
    (run_dir / "diagnostics.json").write_text(
        json.dumps(diagnostics, indent=2),
        encoding="utf-8",
    )

    summary = {
        "run": run_index,
        "cases": len(results),
        "verified_repairs": sum(r.final_status == "VERIFIED_REPAIR" for r in results),
        "verified_repair_rate": verified_repair_rate(results),
        "input_tokens": sum(r.input_tokens for r in results),
        "output_tokens": sum(r.output_tokens for r in results),
        "estimated_cost_usd": sum(r.estimated_cost_usd for r in results),
        "unresolved_cases": [
            r.case_id for r in results if r.final_status != "VERIFIED_REPAIR"
        ],
    }
    (run_dir / "summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )
    return summary


def aggregate(label: str, runs: list[dict]) -> dict:
    rates = [float(run["verified_repair_rate"]) for run in runs]
    return {
        "system": label,
        "runs": len(runs),
        "mean_vrr": mean(rates) if rates else 0.0,
        "min_vrr": min(rates) if rates else 0.0,
        "max_vrr": max(rates) if rates else 0.0,
        "stddev_vrr": pstdev(rates) if len(rates) > 1 else 0.0,
        "mean_verified_repairs": (
            mean([run["verified_repairs"] for run in runs]) if runs else 0.0
        ),
        "total_estimated_cost_usd": sum(
            float(run["estimated_cost_usd"]) for run in runs
        ),
        "unresolved_cases_by_run": {
            f"run_{run['run']:02d}": run["unresolved_cases"] for run in runs
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()

    if args.runs < 2:
        raise SystemExit("--runs must be at least 2 for a variance check")

    cases = load_cases()
    RESULTS_ROOT.mkdir(parents=True, exist_ok=True)

    baseline_runs = []
    preprocessor_runs = []

    for i in range(1, args.runs + 1):
        baseline_runs.append(_run_baseline_round(cases, i))

    for i in range(1, args.runs + 1):
        preprocessor_runs.append(_run_preprocessor_round(cases, i))

    report = {
        "benchmark_cases": len(cases),
        "baseline": aggregate("baseline", baseline_runs),
        "preprocessor": aggregate("log_preprocessor", preprocessor_runs),
    }
    report["delta_mean_vrr_pp"] = (
        report["preprocessor"]["mean_vrr"] - report["baseline"]["mean_vrr"]
    ) * 100.0

    report_path = RESULTS_ROOT / "quality_gate_summary.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=" * 60)
    print("QUALITY GATE")
    print("=" * 60)
    print(f"Baseline mean VRR:      {report['baseline']['mean_vrr'] * 100:.1f}%")
    print(f"Preprocessor mean VRR:  {report['preprocessor']['mean_vrr'] * 100:.1f}%")
    print(f"Mean improvement:       {report['delta_mean_vrr_pp']:.1f} pp")
    print(
        f"Baseline range:         "
        f"{report['baseline']['min_vrr'] * 100:.1f}% - "
        f"{report['baseline']['max_vrr'] * 100:.1f}%"
    )
    print(
        f"Preprocessor range:     "
        f"{report['preprocessor']['min_vrr'] * 100:.1f}% - "
        f"{report['preprocessor']['max_vrr'] * 100:.1f}%"
    )
    print(f"Report: {report_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
