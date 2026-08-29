from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class PatchApplicationError(RuntimeError):
    pass


@dataclass(frozen=True)
class PatchApplyResult:
    file: str
    applied: bool


def apply_search_replace(
    repo_dir: Path,
    *,
    file: str,
    search: str,
    replace: str,
) -> PatchApplyResult:
    if not file or not search:
        raise PatchApplicationError("file and search must be non-empty")

    repo_root = repo_dir.resolve()
    target = (repo_dir / file).resolve()

    try:
        target.relative_to(repo_root)
    except ValueError as exc:
        raise PatchApplicationError("target file escapes repository root") from exc

    if not target.is_file():
        raise PatchApplicationError(f"target file does not exist: {file}")

    original = target.read_text(encoding="utf-8")
    count = original.count(search)

    if count == 0:
        raise PatchApplicationError("SEARCH_BLOCK_NOT_FOUND")
    if count > 1:
        raise PatchApplicationError("AMBIGUOUS_SEARCH_BLOCK")

    updated = original.replace(search, replace, 1)
    target.write_text(updated, encoding="utf-8")

    return PatchApplyResult(file=file, applied=True)
