from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from evaluation.result_schema import CommandResult


def run_python_syntax_check(repo_dir: Path) -> CommandResult:
    command = [sys.executable, "-m", "compileall", "-q", "."]
    proc = subprocess.run(
        command,
        cwd=repo_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    return CommandResult(
        kind="full",
        command=command,
        exit_code=proc.returncode,
        status="PASS" if proc.returncode == 0 else "FAIL",
        duration_seconds=0.0,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )
