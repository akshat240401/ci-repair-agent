from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = PROJECT_ROOT / "results"
OUT_DIR = RESULTS_DIR / "submission"

FINAL_SUMMARY = RESULTS_DIR / "experiments" / "repair_loop" / "summary.json"
FINAL_RESULTS = RESULTS_DIR / "experiments" / "repair_loop" / "results.json"
QUALITY_GATE = RESULTS_DIR / "quality_gate" / "quality_gate_summary.json"
BASELINE_RUN_DIR = RESULTS_DIR / "quality_gate" / "baseline"


def load_json(path: Path) -> Any:
    if not path.exists():
        raise FileNotFoundError(f"Required file missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _sum_usage(rows: list[dict]) -> dict:
    return {
        "input_tokens": sum(int(r.get("input_tokens", 0) or 0) for r in rows),
        "output_tokens": sum(int(r.get("output_tokens", 0) or 0) for r in rows),
        "estimated_cost_usd": sum(
            float(r.get("estimated_cost_usd", 0.0) or 0.0) for r in rows
        ),
    }


def _load_fair_baseline_runs(expected_cases: int) -> list[dict]:
    runs = []
    for path in sorted(BASELINE_RUN_DIR.glob("run_*/results.json")):
        rows = load_json(path)
        if not isinstance(rows, list) or len(rows) != expected_cases:
            continue
        usage = _sum_usage(rows)
        verified = sum(
            r.get("final_status") == "VERIFIED_REPAIR" for r in rows
        )
        runs.append({
            "file": str(path.relative_to(PROJECT_ROOT)),
            "cases": len(rows),
            "verified_repairs": verified,
            "vrr": verified / len(rows),
            **usage,
        })

    if not runs:
        raise RuntimeError(
            "No fair baseline runs found under "
            "results/quality_gate/baseline/run_*/results.json"
        )
    return runs


def build_report() -> dict:
    quality = load_json(QUALITY_GATE)
    final_summary = load_json(FINAL_SUMMARY)
    final_rows = load_json(FINAL_RESULTS)

    expected_cases = int(quality["benchmark_cases"])
    baseline_runs = _load_fair_baseline_runs(expected_cases)
    final_usage = _sum_usage(final_rows)

    return {
        "note": (
            "Costs are approximate evaluator estimates, not billing statements. "
            "Baseline cost comparison includes only the repeated 20-case quality-gate "
            "runs used to compute the development baseline mean VRR. "
            "Final frozen submission numbers must be regenerated from the tagged main commit."
        ),
        "baseline": {
            "benchmark_cases": expected_cases,
            "mean_vrr": quality["baseline"]["mean_vrr"],
            "min_vrr": quality["baseline"]["min_vrr"],
            "max_vrr": quality["baseline"]["max_vrr"],
            "costed_runs": baseline_runs,
            "mean_cost_usd": sum(r["estimated_cost_usd"] for r in baseline_runs) / len(baseline_runs),
            "mean_input_tokens": sum(r["input_tokens"] for r in baseline_runs) / len(baseline_runs),
            "mean_output_tokens": sum(r["output_tokens"] for r in baseline_runs) / len(baseline_runs),
        },
        "final_current_dev_run": {
            "vrr": final_summary["verified_repair_rate"],
            "cases": final_summary["cases"],
            "verified_repairs": final_summary["verified_repairs"],
            "mean_attempts": final_summary["mean_attempts"],
            "retry_cases": final_summary["retry_cases"],
            **final_usage,
        },
    }


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = build_report()
    out = OUT_DIR / "cost_comparison.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    b = report["baseline"]
    f = report["final_current_dev_run"]

    print("=" * 68)
    print("SUBMISSION COST / TOKEN REPORT")
    print("=" * 68)
    print(f"Baseline mean VRR:      {b['mean_vrr'] * 100:.1f}%")
    print(f"Baseline costed runs:   {len(b['costed_runs'])}")
    print(f"Baseline mean input:    {b['mean_input_tokens']:.1f}")
    print(f"Baseline mean output:   {b['mean_output_tokens']:.1f}")
    print(f"Baseline mean cost:     ${b['mean_cost_usd']:.6f}")
    print(f"Final current VRR:      {f['vrr'] * 100:.1f}%")
    print(f"Final input tokens:     {f['input_tokens']}")
    print(f"Final output tokens:    {f['output_tokens']}")
    print(f"Final estimated cost:   ${f['estimated_cost_usd']:.6f}")
    print(f"Report: {out}")
    print("=" * 68)


if __name__ == "__main__":
    main()
