from __future__ import annotations

import base64
import difflib
import io
import json
import os
import shutil
import tempfile
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from evaluation.case_loader import BenchmarkCase
from src.agents.investigation_agent import run_investigation
from src.agents.patch_agent import propose_patch_plan
from src.agents.retry_patch_agent import propose_retry_patch
from src.agents.triage_agent import run_triage
from src.orchestration.no_code_policy import evaluate_no_code_patch
from src.patching.fingerprint import patch_plan_hash
from src.patching.multi_edit import MultiEditError, apply_patch_plan
from src.schemas.benchmark import BenchmarkMetadata
from src.state.failure_signature import failure_signature
from src.state.hashing import repo_state_hash
from src.state.loop_detector import LoopDetector
from src.verification.verifier import verify_patch

MAX_ATTEMPTS = 3
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_EXTRACTED_BYTES = 20 * 1024 * 1024
MAX_FILES = 1200

Progress = Callable[[str, str, dict | None], None]


class UploadValidationError(ValueError):
    pass


def _safe_extract_zip(payload: bytes, dest: Path) -> Path:
    if len(payload) > MAX_UPLOAD_BYTES:
        raise UploadValidationError("Repository ZIP exceeds the 5 MB demo limit.")

    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        infos = [i for i in zf.infolist() if not i.is_dir()]
        if len(infos) > MAX_FILES:
            raise UploadValidationError(f"Repository contains more than {MAX_FILES} files.")
        total = sum(i.file_size for i in infos)
        if total > MAX_EXTRACTED_BYTES:
            raise UploadValidationError("Extracted repository exceeds the 20 MB demo limit.")

        root = dest.resolve()
        for info in zf.infolist():
            # Reject Unix symlinks and path traversal.
            mode = (info.external_attr >> 16) & 0o170000
            if mode == 0o120000:
                raise UploadValidationError("Symlinks are not accepted in uploaded repositories.")
            target = (dest / info.filename).resolve()
            if target != root and root not in target.parents:
                raise UploadValidationError("Unsafe path detected in repository ZIP.")
        zf.extractall(dest)

    children = [p for p in dest.iterdir() if p.name not in {"__MACOSX"}]
    if len(children) == 1 and children[0].is_dir():
        return children[0]
    return dest


def _make_case(repo_dir: Path, failing_log: str, targeted_test: str, work: Path) -> BenchmarkCase:
    work.mkdir(parents=True, exist_ok=True)
    log_path = work / "failing_log.txt"
    metadata_path = work / "metadata.json"
    log_path.write_text(failing_log, encoding="utf-8")

    metadata = BenchmarkMetadata(
        case_id="case_999",
        title="Uploaded repository repair",
        language="python",
        python_version="3.11",
        failure_family="uploaded",
        expected_failure_type="UNKNOWN",
        targeted_test=targeted_test,
        full_test_command="pytest -q",
        repairable=True,
        challenging=True,
        notes="User supplied through the web interface.",
    )
    metadata_path.write_text(json.dumps(metadata.model_dump(), indent=2), encoding="utf-8")
    return BenchmarkCase(
        case_id=metadata.case_id,
        case_dir=work,
        repo_dir=repo_dir,
        log_path=log_path,
        metadata_path=metadata_path,
        metadata=metadata,
    )


def _feedback(v) -> dict:
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


def _repo_text_files(root: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        if any(part in {".git", ".venv", "__pycache__", ".pytest_cache"} for part in p.parts):
            continue
        try:
            if p.stat().st_size > 300_000:
                continue
            result[rel] = p.read_text(encoding="utf-8").splitlines(keepends=True)
        except (UnicodeDecodeError, OSError):
            continue
    return result


def _diff_repos(before: Path, after: Path) -> str:
    old = _repo_text_files(before)
    new = _repo_text_files(after)
    chunks: list[str] = []
    for name in sorted(set(old) | set(new)):
        if old.get(name) == new.get(name):
            continue
        chunks.extend(
            difflib.unified_diff(
                old.get(name, []),
                new.get(name, []),
                fromfile=f"a/{name}",
                tofile=f"b/{name}",
            )
        )
    return "".join(chunks)


def _zip_repo(root: Path) -> str:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in sorted(root.rglob("*")):
            if not p.is_file():
                continue
            if any(part in {".git", ".venv", "__pycache__", ".pytest_cache"} for part in p.parts):
                continue
            zf.write(p, p.relative_to(root).as_posix())
    return base64.b64encode(buf.getvalue()).decode("ascii")


def run_uploaded_repair(
    *,
    repo_zip: bytes,
    failing_log: str,
    targeted_test: str,
    progress: Progress,
) -> dict:
    if not failing_log.strip():
        raise UploadValidationError("A failing CI/test log is required.")
    if not targeted_test.strip():
        raise UploadValidationError("A targeted pytest node is required, for example tests/test_api.py::test_contract.")

    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="ci_repair_web_") as td:
        work = Path(td)
        uploaded = work / "uploaded"
        uploaded.mkdir()
        repo_dir = _safe_extract_zip(repo_zip, uploaded)
        case = _make_case(repo_dir, failing_log, targeted_test, work)

        before = work / "before"
        shutil.copytree(repo_dir, before)

        progress("triage", "Classifying the failure and likely repair scope", None)
        triage, _ = run_triage(case)
        progress("triage", "Triage complete", triage.model_dump())

        no_code = evaluate_no_code_patch(triage)
        if no_code is not None:
            return {
                "final_status": "NO_CODE_PATCH_REQUIRED",
                "reason": no_code.reason,
                "triage": triage.model_dump(),
                "latency_seconds": time.perf_counter() - started,
                "attempts": 0,
                "files_modified": 0,
                "diff": "",
                "repaired_zip_b64": None,
            }

        progress("investigate", "Inspecting repository evidence with bounded tools", None)
        investigation, _, trajectory = run_investigation(case, triage)
        progress("investigate", "Investigation complete", {
            "root_cause": investigation.root_cause,
            "target_files": investigation.target_files,
            "trajectory": trajectory,
        })

        progress("plan", "Generating a structured multi-file repair plan", None)
        plan, _ = propose_patch_plan(case, triage, investigation)
        progress("plan", "Repair plan ready", plan.model_dump())

        # Operate on a copy so the uploaded snapshot remains unchanged.
        repair_repo = work / "repair_repo"
        shutil.copytree(repo_dir, repair_repo)
        repair_case = _make_case(repair_repo, failing_log, targeted_test, work / "repair_case")
        detector = LoopDetector()
        detector.record_repo_state(repo_state_hash(repair_repo))
        current_plan = plan
        attempts: list[dict] = []
        stopped_reason = None
        files_modified = 0
        last_verification = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            progress("patch", f"Applying repair attempt {attempt}/{MAX_ATTEMPTS}", current_plan.model_dump())
            p_hash = patch_plan_hash(current_plan)
            if detector.record_patch(p_hash):
                stopped_reason = "DUPLICATE_PATCH"
                break

            snapshot = work / f"snapshot_{attempt}"
            shutil.copytree(repair_repo, snapshot)
            record: dict = {"attempt": attempt, "patch_plan": current_plan.model_dump()}

            try:
                applied = apply_patch_plan(repair_repo, current_plan)
                files_modified = applied.files_modified
            except MultiEditError as exc:
                record["patch_error"] = str(exc)
                attempts.append(record)
                if attempt == MAX_ATTEMPTS:
                    stopped_reason = "MAX_ATTEMPTS"
                    break
                shutil.rmtree(repair_repo)
                shutil.copytree(snapshot, repair_repo)
                progress("retry", "Patch application failed; requesting a bounded retry", {"error": str(exc)})
                current_plan, _ = propose_retry_patch(
                    repair_case, triage, investigation, current_plan,
                    {"patch_application_error": str(exc)},
                )
                continue

            progress("verify", "Running syntax, targeted test, and full regression verification", None)
            verification = verify_patch(repair_repo, targeted_test)
            last_verification = verification
            record["verification"] = _feedback(verification)
            attempts.append(record)

            if verification.verified:
                stopped_reason = "VERIFIED_REPAIR"
                break

            repo_hash = repo_state_hash(repair_repo)
            sig = failure_signature(verification.full_suite or verification.targeted or verification.syntax)
            if detector.record_repo_state(repo_hash):
                stopped_reason = "REPEATED_REPO_STATE"
                break
            repeated_failure = detector.record_failure(sig)
            if detector.has_two_state_oscillation():
                stopped_reason = "OSCILLATION"
                break
            if repeated_failure:
                stopped_reason = "NO_PROGRESS"
                break
            if attempt == MAX_ATTEMPTS:
                stopped_reason = "MAX_ATTEMPTS"
                break

            progress("retry", "Verification failed; using deterministic feedback for another attempt", _feedback(verification))
            fb = _feedback(verification)
            shutil.rmtree(repair_repo)
            shutil.copytree(snapshot, repair_repo)
            current_plan, _ = propose_retry_patch(repair_case, triage, investigation, current_plan, fb)

        verified = bool(last_verification and last_verification.verified)
        final_status = "VERIFIED_REPAIR" if verified else "UNRESOLVED"
        progress("done", f"Repair finished with {final_status}", {"stopped_reason": stopped_reason})

        return {
            "final_status": final_status,
            "stopped_reason": stopped_reason,
            "root_cause": investigation.root_cause,
            "target_files": investigation.target_files,
            "triage": triage.model_dump(),
            "investigation": investigation.model_dump(),
            "attempts": attempts,
            "attempt_count": len(attempts),
            "files_modified": files_modified,
            "syntax_passed": bool(last_verification and last_verification.syntax_passed),
            "targeted_test_passed": bool(last_verification and last_verification.targeted_test_passed),
            "full_suite_passed": bool(last_verification and last_verification.full_suite_passed),
            "diff": _diff_repos(before, repair_repo),
            "repaired_zip_b64": _zip_repo(repair_repo) if verified else None,
            "latency_seconds": time.perf_counter() - started,
        }
