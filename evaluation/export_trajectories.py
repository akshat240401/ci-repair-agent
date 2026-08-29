from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESULTS = PROJECT_ROOT / "results"
OUT = PROJECT_ROOT / "trajectories"

INV_DIAGNOSTICS = RESULTS / "experiments" / "investigation" / "diagnostics.json"
LOOP_DIAGNOSTICS = RESULTS / "experiments" / "repair_loop" / "diagnostics.json"
LOOP_RESULTS = RESULTS / "experiments" / "repair_loop" / "results.json"

PROFILES = {
    "trajectory_01_simple_repair.json": "case_001",
    "trajectory_02_multi_file_repair.json": "case_013",
    "trajectory_03_regression_sensitive.json": "case_010",
    "trajectory_04_config_contract.json": "case_020",
}


def load(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def by_case(rows: list[dict] | None) -> dict[str, dict]:
    if not rows:
        return {}
    return {r.get("case_id"): r for r in rows if isinstance(r, dict) and r.get("case_id")}


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        clean = {}
        for key, item in value.items():
            lower = key.lower()
            if any(marker in lower for marker in ("api_key", "authorization", "secret", "token_value")):
                clean[key] = "[REDACTED]"
            else:
                clean[key] = sanitize(item)
        return clean
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, str) and "sk-" in value:
        return "[REDACTED_POTENTIAL_SECRET]"
    return value


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    inv = by_case(load(INV_DIAGNOSTICS, []))
    loop = by_case(load(LOOP_DIAGNOSTICS, []))
    loop_results = by_case(load(LOOP_RESULTS, []))
    manifest = []

    for filename, case_id in PROFILES.items():
        artifact = sanitize({
            "artifact_type": "representative_agent_trajectory",
            "source": "recorded benchmark diagnostics",
            "case_id": case_id,
            "agents": ["triage", "investigation", "patch"],
            "investigation": inv.get(case_id),
            "repair_loop": loop.get(case_id),
            "result": loop_results.get(case_id),
        })
        (OUT / filename).write_text(json.dumps(artifact, indent=2), encoding="utf-8")
        manifest.append({"file": filename, "case_id": case_id, "source": "recorded benchmark diagnostics"})

    proofs = [
        (
            "trajectory_05_retry_recovery_proof.json",
            {
                "artifact_type": "deterministic_behavioral_proof",
                "source": "tests/test_repair_loop_retry.py",
                "profile": "forced retry recovery",
                "expected_sequence": [
                    "attempt_1_patch_applies",
                    "targeted_test_fails",
                    "verification_feedback_generated",
                    "retry_patch_requested",
                    "attempt_2_patch_applies",
                    "targeted_test_passes",
                    "full_suite_passes",
                    "VERIFIED_REPAIR",
                ],
                "note": "Deterministic proof; current live 20-case run repaired all cases on attempt 1.",
            },
        ),
        (
            "trajectory_06_circuit_breaker_proof.json",
            {
                "artifact_type": "deterministic_behavioral_proof",
                "source": "tests/test_repair_loop_circuit_breaker.py and tests/test_loop_detector.py",
                "profile": "unresolved/circuit-breaker safety",
                "demonstrated_guards": [
                    "duplicate patch detection",
                    "repeated repository state detection",
                    "no-progress repeated failure detection",
                    "A -> B -> A oscillation detection",
                    "maximum three repair attempts",
                ],
                "note": "Deterministic safety proof; not presented as a live LLM failure.",
            },
        ),
        (
            "trajectory_07_config_only_no_code_bypass_proof.json",
            {
                "artifact_type": "deterministic_behavioral_proof",
                "source": "tests/test_no_code_patch_policy.py",
                "profile": "config-only no-code bypass",
                "input_triage": {
                    "failure_type": "ENVIRONMENT_CONFIG",
                    "target_files": [],
                    "example_evidence": "CI runner is missing required environment variable SERVICE_TOKEN",
                },
                "policy": "Only ENVIRONMENT_CONFIG failures with zero repository target files are eligible for deterministic bypass.",
                "result": {
                    "status": "NO_CODE_PATCH_REQUIRED",
                    "code_patch_attempted": False,
                },
                "negative_controls": [
                    "ENVIRONMENT_CONFIG with repository target files continues through normal repair.",
                    "LOGIC_BUG never uses the no-code bypass.",
                ],
                "note": "Deterministic policy proof, labeled separately from live benchmark trajectories.",
            },
        ),
    ]

    for filename, artifact in proofs:
        (OUT / filename).write_text(json.dumps(artifact, indent=2), encoding="utf-8")
        manifest.append({"file": filename, "source": artifact["source"]})

    (OUT / "manifest.json").write_text(
        json.dumps({"trajectories": manifest}, indent=2),
        encoding="utf-8",
    )

    print("=" * 68)
    print("TRAJECTORY EXPORT")
    print("=" * 68)
    for item in manifest:
        print(f"{item['file']} | {item['source']}")
    print(f"Manifest: {OUT / 'manifest.json'}")
    print("=" * 68)


if __name__ == "__main__":
    main()
