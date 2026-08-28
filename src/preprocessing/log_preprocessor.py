from __future__ import annotations

import re


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
PYTEST_PROGRESS_RE = re.compile(r"^\s*[.FsExX]+\s*(?:\[\s*\d+%\])?\s*$")
SEPARATOR_RE = re.compile(r"^[=_-]{10,}\s*$")


def preprocess_log(raw: str) -> str:
    """
    Deterministic, conservative pytest-log cleanup.

    Keeps failure evidence (tracebacks, assertions, file/line references,
    short summaries) while removing obvious display noise and duplicate
    blank/separator lines.
    """
    text = ANSI_RE.sub("", raw.replace("\r\n", "\n").replace("\r", "\n"))

    output: list[str] = []
    previous_blank = False
    previous_separator = False

    for line in text.split("\n"):
        stripped = line.rstrip()

        if PYTEST_PROGRESS_RE.fullmatch(stripped):
            continue

        is_blank = not stripped.strip()
        if is_blank:
            if previous_blank:
                continue
            output.append("")
            previous_blank = True
            previous_separator = False
            continue

        is_separator = bool(SEPARATOR_RE.fullmatch(stripped.strip()))
        if is_separator:
            if previous_separator:
                continue
            output.append(stripped)
            previous_separator = True
            previous_blank = False
            continue

        output.append(stripped)
        previous_blank = False
        previous_separator = False

    # Remove duplicate adjacent non-empty lines caused by repeated CI wrappers.
    deduped: list[str] = []
    for line in output:
        if line and deduped and line == deduped[-1]:
            continue
        deduped.append(line)

    return "\n".join(deduped).strip() + "\n"
