from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from evaluation.runner import run_full_suite, run_targeted_test
from src.verification.syntax_check import run_python_syntax_check


@dataclass(frozen=True)
class VerificationResult:
    syntax_passed: bool
    targeted_test_passed: bool
    full_suite_passed: bool


def verify_patch(repo_dir: Path, targeted_test: str) -> VerificationResult:
    syntax = run_python_syntax_check(repo_dir)
    if syntax.status != "PASS":
        return VerificationResult(False, False, False)

    targeted = run_targeted_test(repo_dir, targeted_test)
    if targeted.status != "PASS":
        return VerificationResult(True, False, False)

    full_suite = run_full_suite(repo_dir)

    return VerificationResult(
        syntax_passed=True,
        targeted_test_passed=True,
        full_suite_passed=(full_suite.status == "PASS"),
    )
