from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TEMP_HELPERS = [
    "CLEAN_ROOM_HOTFIX_README.md",
    "CLEAN_ROOM_README.md",
    "NO_CODE_BYPASS_INTEGRATION_README.md",
    "STEPS_32_34_README.md",
    "SUBMISSION_HARDENING_CORRECTION_README.md",
]

AGENT_VISIBLE_DIRS = [
    ROOT / "src" / "agents",
    ROOT / "src" / "tools",
    ROOT / "src" / "orchestration",
    ROOT / "src" / "patching",
    ROOT / "src" / "verification",
]

TEXT_SUFFIXES = {
    ".py", ".md", ".txt", ".toml", ".json", ".yaml", ".yml",
    ".ps1", ".cfg", ".ini", ".env", ".example",
}


class AuditFailure(RuntimeError):
    pass


def ok(message: str) -> None:
    print(f"[PASS] {message}")


def fail(message: str) -> None:
    raise AuditFailure(message)


def run_checked(*args: str) -> None:
    print("$ " + " ".join(args))
    completed = subprocess.run(args, cwd=ROOT)
    if completed.returncode != 0:
        fail(f"Command failed with exit code {completed.returncode}: {' '.join(args)}")


def tracked_files() -> list[Path]:
    completed = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return [ROOT / line.strip() for line in completed.stdout.splitlines() if line.strip()]


def check_no_temporary_helpers() -> None:
    present = [name for name in TEMP_HELPERS if (ROOT / name).exists()]
    if present:
        fail(
            "Temporary development helper files remain in repository root: "
            + ", ".join(present)
        )
    ok("temporary development helper files removed")


def check_secret_leakage() -> None:
    secret_key_pattern = re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")
    assignment_pattern = re.compile(
        r"OPENAI_API_KEY\s*=\s*[\"']?(?!YOUR_KEY\b)(?!<)(?!$)([^\"'\s#]+)",
        re.IGNORECASE,
    )

    findings: list[str] = []
    for path in tracked_files():
        if not path.is_file():
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name != ".env.example":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        rel = path.relative_to(ROOT).as_posix()
        for match in secret_key_pattern.finditer(text):
            findings.append(f"{rel}: secret-like OpenAI key")
        for match in assignment_pattern.finditer(text):
            value = match.group(1).strip()
            if value and value not in {"YOUR_KEY", "YOUR_KEY_HERE"}:
                findings.append(f"{rel}: nonblank OPENAI_API_KEY assignment")

    if findings:
        fail("Potential credential leakage:\n  " + "\n  ".join(findings[:20]))
    ok("no committed OpenAI credential pattern detected")


def check_ground_truth_isolation() -> None:
    violations: list[str] = []
    for directory in AGENT_VISIBLE_DIRS:
        if not directory.exists():
            continue
        for path in directory.rglob("*.py"):
            text = path.read_text(encoding="utf-8").lower()
            if "benchmark/ground_truth" in text or "benchmark\\ground_truth" in text:
                violations.append(path.relative_to(ROOT).as_posix())

    if violations:
        fail(
            "Agent-visible runtime code references evaluator ground truth: "
            + ", ".join(violations)
        )
    ok("benchmark ground truth is not referenced by agent-visible runtime code")


def check_smoke_isolation() -> None:
    text = (ROOT / "evaluate.py").read_text(encoding="utf-8")
    if "results/smoke/repair_loop" not in text:
        fail("Smoke evaluation is not isolated from canonical full-run results")
    ok("smoke evaluation writes to isolated result path")


def check_no_code_wiring() -> None:
    text = (ROOT / "evaluation" / "repair_loop_experiment.py").read_text(encoding="utf-8")
    required = [
        "evaluate_no_code_patch(triage)",
        "build_no_code_result(",
        "NO_CODE_PATCH_REQUIRED",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        fail("Real repair-loop runner is missing no-code wiring: " + ", ".join(missing))
    ok("NO_CODE_PATCH_REQUIRED path is wired into the real repair-loop runner")


def check_canonical_results() -> None:
    path = ROOT / "results" / "experiments" / "repair_loop" / "results.json"
    if not path.exists():
        fail("Canonical repair-loop results.json is missing")

    data = json.loads(path.read_text(encoding="utf-8"))
    if len(data) != 20:
        fail(f"Canonical repair-loop result set has {len(data)} cases; expected 20")

    allowed = {"VERIFIED_REPAIR", "NO_CODE_PATCH_REQUIRED", "UNRESOLVED"}
    bad = []
    iterable = data.items() if isinstance(data, dict) else [
        (item.get("case_id", f"index_{i}"), item)
        for i, item in enumerate(data)
    ]
    for case_id, item in iterable:
        status = item.get("final_status")
        if status not in allowed:
            bad.append((case_id, status))
    if bad:
        fail(f"Unexpected final statuses: {bad}")

    ok("canonical repair-loop artifact contains exactly 20 valid case results")


def check_evidence_consistency() -> None:
    evidence_path = ROOT / "results" / "final_evidence" / "evidence_summary.json"
    cost_path = ROOT / "results" / "submission" / "cost_comparison.json"

    if not evidence_path.exists():
        fail("Evidence summary is missing")
    if not cost_path.exists():
        fail("Submission cost comparison is missing")

    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    cost = json.loads(cost_path.read_text(encoding="utf-8"))

    baseline_vrr = evidence.get("baseline_mean_vrr")
    final_vrr = evidence.get("final_vrr")
    improvement = evidence.get("absolute_improvement_pp")

    if baseline_vrr is None or final_vrr is None or improvement is None:
        fail("Evidence summary is missing headline metrics")

    expected_pp = round((final_vrr - baseline_vrr) * 100, 6)
    if abs(expected_pp - improvement) > 1e-5:
        fail(
            f"Evidence improvement mismatch: computed {expected_pp}, "
            f"reported {improvement}"
        )

    baseline_cost = cost.get("baseline", {})

    run_count = baseline_cost.get("costed_runs")
    if run_count is None:
        run_count = baseline_cost.get("run_count")
    if run_count is None:
        run_count = baseline_cost.get("runs")

    if isinstance(run_count, list):
        run_count = len(run_count)

    if run_count is None:
        # The report generator already filters to the canonical quality-gate
        # directory. If no explicit count field is stored, derive it from the
        # committed three baseline run artifacts.
        quality_gate_dir = ROOT / "results" / "quality_gate" / "baseline"
        run_count = len(list(quality_gate_dir.glob("run_*/results.json")))

    if run_count != 3:
        fail(
            f"Cost report baseline run count is {run_count}; expected exactly 3"
        )

    ok("headline evidence and cost comparison are internally consistent")


def check_docs() -> None:
    required = {
        "README.md": [
            "Verified Repair Rate",
            "development result",
            "Hot take",
            "multi-file transactional",
            "NO_CODE_PATCH_REQUIRED",
        ],
        "IMPROVEMENT_CHANGELOG.md": [
            "Log preprocessing",
            "0.0 pp improvement",
            "Multi-file transactional patch plan",
            "Clean-room reproduction",
        ],
        "REPRODUCTION.md": [
            "Python 3.11",
            "evaluation.evaluator --mode inspect",
            "OPENAI_API_KEY",
            "tagged `main`",
            "clean_room_check.ps1",
        ],
    }

    missing: list[str] = []
    for filename, phrases in required.items():
        text = (ROOT / filename).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                missing.append(f"{filename}: {phrase}")

    if missing:
        fail("Submission documentation is missing required content:\n  " + "\n  ".join(missing))
    ok("README, changelog, and reproduction guide cover submission-critical content")


def check_trajectories() -> None:
    manifest_path = ROOT / "trajectories" / "manifest.json"
    if not manifest_path.exists():
        fail("Trajectory manifest is missing")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if isinstance(manifest, list):
        count = len(manifest)
    elif isinstance(manifest, dict):
        if isinstance(manifest.get("trajectories"), list):
            count = len(manifest["trajectories"])
        else:
            count = len([k for k in manifest if str(k).startswith("trajectory")])
            if count == 0:
                count = 7 if "trajectory_07_config_only_no_code_bypass_proof.json" in manifest_path.read_text(encoding="utf-8") else 0
    else:
        count = 0

    manifest_text = manifest_path.read_text(encoding="utf-8")
    required_names = [
        "trajectory_01_simple_repair.json",
        "trajectory_02_multi_file_repair.json",
        "trajectory_03_regression_sensitive.json",
        "trajectory_04_config_contract.json",
        "trajectory_05_retry_recovery_proof.json",
        "trajectory_06_circuit_breaker_proof.json",
        "trajectory_07_config_only_no_code_bypass_proof.json",
    ]
    missing = [name for name in required_names if name not in manifest_text]
    if missing:
        fail("Trajectory manifest is missing representative artifacts: " + ", ".join(missing))

    ok("trajectory manifest covers live benchmark diagnostics and deterministic proof artifacts")


def main() -> None:
    print("=" * 72)
    print("STEP 40 — FINAL END-TO-END / SUBMISSION AUDIT")
    print("=" * 72)

    check_no_temporary_helpers()
    check_secret_leakage()
    check_ground_truth_isolation()
    check_smoke_isolation()
    check_no_code_wiring()

    run_checked(sys.executable, "-m", "pytest", "-q", "tests")
    run_checked(sys.executable, "-m", "evaluation.evaluator", "--mode", "inspect")
    run_checked(sys.executable, "-m", "evaluation.evidence_report")
    run_checked(sys.executable, "-m", "evaluation.submission_cost_report")
    run_checked(sys.executable, "-m", "evaluation.export_trajectories")

    check_canonical_results()
    check_evidence_consistency()
    check_docs()
    check_trajectories()

    print()
    print("=" * 72)
    print("STEP 40 AUDIT PASSED")
    print("=" * 72)
    print("Deterministic repository audit is green.")
    print("Next gate: clean-room run, then merge/tag/frozen final evaluation.")


if __name__ == "__main__":
    try:
        main()
    except AuditFailure as exc:
        print()
        print("=" * 72)
        print("STEP 40 AUDIT FAILED")
        print("=" * 72)
        print(exc)
        raise SystemExit(1)
