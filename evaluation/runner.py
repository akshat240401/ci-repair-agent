from __future__ import annotations
import os, subprocess, sys, time
from pathlib import Path
from evaluation.result_schema import CommandResult
DEFAULT_TIMEOUT_SECONDS=30
def _run_pytest(repo_dir: Path, pytest_args: list[str], *, kind: str, timeout_seconds: int=DEFAULT_TIMEOUT_SECONDS) -> CommandResult:
    command=[sys.executable, "-m", "pytest", "-q", *pytest_args]
    env=os.environ.copy(); old=env.get("PYTHONPATH","")
    env["PYTHONPATH"]=str(repo_dir) if not old else str(repo_dir)+os.pathsep+old
    started=time.perf_counter()
    try:
        proc=subprocess.run(command,cwd=repo_dir,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout_seconds)
        duration=time.perf_counter()-started
        return CommandResult(kind=kind,command=command,exit_code=proc.returncode,status="PASS" if proc.returncode==0 else "FAIL",duration_seconds=duration,stdout=proc.stdout,stderr=proc.stderr)
    except subprocess.TimeoutExpired as exc:
        duration=time.perf_counter()-started
        stdout=exc.stdout if isinstance(exc.stdout,str) else ""; stderr=exc.stderr if isinstance(exc.stderr,str) else ""
        return CommandResult(kind=kind,command=command,exit_code=None,status="ERROR",duration_seconds=duration,stdout=stdout,stderr=(stderr+f"\nTimed out after {timeout_seconds}s").strip())
def run_targeted_test(repo_dir: Path,targeted_test: str,*,timeout_seconds:int=DEFAULT_TIMEOUT_SECONDS)->CommandResult:
    return _run_pytest(repo_dir,[targeted_test],kind="targeted",timeout_seconds=timeout_seconds)
def run_full_suite(repo_dir: Path,*,timeout_seconds:int=DEFAULT_TIMEOUT_SECONDS)->CommandResult:
    return _run_pytest(repo_dir,[],kind="full",timeout_seconds=timeout_seconds)
