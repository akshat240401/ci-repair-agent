from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT_ROOT / "results"
OUT_DIR = RESULTS / "final_evidence"

HARD_CASES = ["case_003", "case_010", "case_013", "case_015", "case_020"]


def _load(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Required evidence file missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_list(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Required evidence file missing: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(f"Expected list in {path}")
    return data


def _index_by_case(rows: list[dict]) -> dict[str, dict]:
    return {row["case_id"]: row for row in rows}


def build_report() -> tuple[dict, str]:
    quality_gate = _load(
        RESULTS / "quality_gate" / "quality_gate_summary.json"
    )
    triage = _load(
        RESULTS / "experiments" / "triage" / "summary.json"
    )
    investigation = _load(
        RESULTS / "experiments" / "investigation" / "summary.json"
    )
    patch_agent = _load(
        RESULTS / "experiments" / "patch_agent" / "summary.json"
    )
    repair_loop = _load(
        RESULTS / "experiments" / "repair_loop" / "summary.json"
    )

    baseline_runs = quality_gate["baseline"]
    preprocessor_runs = quality_gate["preprocessor"]

    patch_results = _index_by_case(
        _load_list(RESULTS / "experiments" / "patch_agent" / "results.json")
    )
    loop_results = _index_by_case(
        _load_list(RESULTS / "experiments" / "repair_loop" / "results.json")
    )

    hard_case_results = {}
    for case_id in HARD_CASES:
        hard_case_results[case_id] = {
            "patch_agent_status": patch_results[case_id]["final_status"],
            "repair_loop_status": loop_results[case_id]["final_status"],
            "repair_loop_attempts": loop_results[case_id]["attempts"],
        }

    keep_remove = [
        {
            "experiment": "log_preprocessor",
            "decision": "REMOVE_AS_PRIMARY_IMPROVEMENT",
            "evidence": (
                f"Repeated quality gate showed {preprocessor_runs['mean_vrr'] * 100:.1f}% "
                f"mean VRR versus {baseline_runs['mean_vrr'] * 100:.1f}% baseline "
                f"({quality_gate['delta_mean_vrr_pp']:.1f} pp)."
            ),
        },
        {
            "experiment": "triage_agent",
            "decision": "KEEP_AS_ROUTING_COMPONENT",
            "evidence": (
                f"Triage classification accuracy was {triage['triage_accuracy'] * 100:.1f}%, "
                f"but repair VRR was {triage['verified_repair_rate'] * 100:.1f}%; "
                "useful for structured routing, not sufficient as a standalone repair improvement."
            ),
        },
        {
            "experiment": "investigation_agent",
            "decision": "KEEP",
            "evidence": (
                f"Root-file hit rate reached {investigation['root_file_hit_rate'] * 100:.1f}% "
                f"with {investigation['mean_tool_calls']:.2f} mean tool calls."
            ),
        },
        {
            "experiment": "multi_file_patch_agent",
            "decision": "KEEP_PRIMARY_WIN",
            "evidence": (
                f"Verified Repair Rate reached {patch_agent['verified_repair_rate'] * 100:.1f}% "
                f"with {patch_agent['verified_repairs']}/{patch_agent['cases']} verified repairs."
            ),
        },
        {
            "experiment": "verified_repair_loop",
            "decision": "KEEP_FOR_SAFETY_AND_ROBUSTNESS",
            "evidence": (
                f"Verified Repair Rate was {repair_loop['verified_repair_rate'] * 100:.1f}%. "
                "Retry/circuit-breaker behavior is separately demonstrated by deterministic tests."
            ),
        },
    ]

    baseline_mean = baseline_runs["mean_vrr"]
    final_vrr = repair_loop["verified_repair_rate"]

    report = {
        "benchmark_cases": quality_gate["benchmark_cases"],
        "baseline_mean_vrr": baseline_mean,
        "baseline_range": [
            baseline_runs["min_vrr"],
            baseline_runs["max_vrr"],
        ],
        "final_vrr": final_vrr,
        "absolute_improvement_pp": (final_vrr - baseline_mean) * 100.0,
        "relative_error_reduction": (
            0.0
            if baseline_mean >= 1.0
            else (
                (1.0 - baseline_mean) - (1.0 - final_vrr)
            ) / (1.0 - baseline_mean)
        ),
        "keep_remove_decisions": keep_remove,
        "hard_case_results": hard_case_results,
        "failure_mode_analysis": [
            {
                "mode": "one-shot single-file repair cannot express cross-file contracts",
                "observed_in": ["case_013", "case_015"],
                "resolution": "multi-file transactional patch planning",
            },
            {
                "mode": "targeted test can pass while regression suite fails",
                "observed_in": ["case_010"],
                "resolution": "full-suite verification gate plus retry feedback path",
            },
            {
                "mode": "model vocabulary can violate strict schemas despite correct semantics",
                "observed_in": ["case_020"],
                "resolution": "canonical schema normalization with deterministic fallback",
            },
            {
                "mode": "stochastic LLM runs can make apparent improvements misleading",
                "observed_in": ["quality_gate"],
                "resolution": "repeated baseline/experiment runs before accepting a change",
            },
        ],
        "hot_take": (
            "The strongest reliability gains did not come from adding more prompting. "
            "They came from separating judgment from proof: agents investigate and propose, "
            "while deterministic code applies exact edits, runs syntax/targeted/regression checks, "
            "and stops loops. Multi-file transactional repair was the decisive capability."
        ),
    }

    md = f"""# Evidence Summary

## Headline result

- Benchmark: **{report['benchmark_cases']} synthetic Python CI repair cases**
- Repeated baseline mean VRR: **{baseline_mean * 100:.1f}%**
- Baseline range: **{baseline_runs['min_vrr'] * 100:.1f}%-{baseline_runs['max_vrr'] * 100:.1f}%**
- Final verified repair loop VRR: **{final_vrr * 100:.1f}%**
- Absolute improvement: **{report['absolute_improvement_pp']:.1f} percentage points**

## Keep / remove decisions

"""
    for item in keep_remove:
        md += (
            f"- **{item['experiment']} - {item['decision']}**: "
            f"{item['evidence']}\n"
        )

    md += "\n## Hard-case evaluation\n\n"
    for case_id, result in hard_case_results.items():
        md += (
            f"- **{case_id}**: patch agent={result['patch_agent_status']}, "
            f"repair loop={result['repair_loop_status']}, "
            f"attempts={result['repair_loop_attempts']}\n"
        )

    md += "\n## Failure-mode analysis\n\n"
    for item in report["failure_mode_analysis"]:
        md += (
            f"- **{item['mode']}** -> {item['resolution']} "
            f"(observed in: {', '.join(item['observed_in'])})\n"
        )

    md += f"\n## Hot take\n\n{report['hot_take']}\n"

    return report, md


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report, md = build_report()

    json_path = OUT_DIR / "evidence_summary.json"
    md_path = OUT_DIR / "EVIDENCE_SUMMARY.md"

    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(md, encoding="utf-8")

    print("=" * 60)
    print("EVIDENCE REPORT")
    print("=" * 60)
    print(f"Baseline mean VRR:     {report['baseline_mean_vrr'] * 100:.1f}%")
    print(f"Final VRR:             {report['final_vrr'] * 100:.1f}%")
    print(f"Improvement:           {report['absolute_improvement_pp']:.1f} pp")
    print(f"JSON: {json_path}")
    print(f"Markdown: {md_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()
