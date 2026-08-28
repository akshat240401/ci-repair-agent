from __future__ import annotations

from pathlib import Path

from evaluation.case_loader import BenchmarkCase


ALLOWED_SUFFIXES = {".py", ".json", ".toml", ".yaml", ".yml", ".ini", ".cfg", ".txt"}
MAX_FILE_CHARS = 20_000


def build_repository_context(case: BenchmarkCase) -> str:
    sections: list[str] = []

    for path in sorted(p for p in case.repo_dir.rglob("*") if p.is_file()):
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            continue

        rel = path.relative_to(case.repo_dir).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > MAX_FILE_CHARS:
            text = text[:MAX_FILE_CHARS] + "\n...[TRUNCATED]..."

        sections.append(f"===== FILE: {rel} =====\n{text}")

    return "\n\n".join(sections)


def build_baseline_input(case: BenchmarkCase) -> str:
    failing_log = case.log_path.read_text(encoding="utf-8", errors="replace")
    repo_context = build_repository_context(case)

    return (
        "===== FAILING CI LOG =====\n"
        f"{failing_log}\n\n"
        "===== REPOSITORY =====\n"
        f"{repo_context}"
    )
