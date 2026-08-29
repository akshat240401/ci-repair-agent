from __future__ import annotations

from pathlib import Path
import subprocess


def _git(repo_dir: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=repo_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if proc.returncode != 0:
        return "GIT_CONTEXT_UNAVAILABLE"

    return proc.stdout.strip() or "NO_CHANGES"


def get_recent_git_diff(repo_dir: Path) -> str:
    return _git(repo_dir, "diff", "HEAD~1", "HEAD", "--")


def get_changed_files(repo_dir: Path) -> str:
    return _git(repo_dir, "diff", "--name-only", "HEAD~1", "HEAD", "--")
