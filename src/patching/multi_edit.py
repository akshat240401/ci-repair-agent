from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.schemas.patch_plan import PatchPlan


class MultiEditError(RuntimeError):
    pass


@dataclass(frozen=True)
class AppliedPatch:
    files_modified: int
    edits_applied: int


def _safe_target(repo_dir: Path, rel_path: str) -> Path:
    root = repo_dir.resolve()
    target = (repo_dir / rel_path).resolve()

    try:
        target.relative_to(root)
    except ValueError as exc:
        raise MultiEditError(
            f"target file escapes repository root: {rel_path}"
        ) from exc

    if not target.is_file():
        raise MultiEditError(f"target file does not exist: {rel_path}")

    return target


def validate_patch_plan(repo_dir: Path, plan: PatchPlan) -> None:
    """
    Validate the complete plan before modifying any file.

    This makes application transactional: either every edit is valid, or
    nothing is written.
    """
    simulated: dict[Path, str] = {}

    for index, edit in enumerate(plan.edits, start=1):
        target = _safe_target(repo_dir, edit.file)

        if target not in simulated:
            simulated[target] = target.read_text(encoding="utf-8")

        current = simulated[target]
        count = current.count(edit.search)

        if count == 0:
            raise MultiEditError(
                f"edit {index}: SEARCH_BLOCK_NOT_FOUND in {edit.file}"
            )
        if count > 1:
            raise MultiEditError(
                f"edit {index}: AMBIGUOUS_SEARCH_BLOCK in {edit.file}"
            )

        simulated[target] = current.replace(edit.search, edit.replace, 1)


def apply_patch_plan(repo_dir: Path, plan: PatchPlan) -> AppliedPatch:
    validate_patch_plan(repo_dir, plan)

    contents: dict[Path, str] = {}

    for edit in plan.edits:
        target = _safe_target(repo_dir, edit.file)

        if target not in contents:
            contents[target] = target.read_text(encoding="utf-8")

        contents[target] = contents[target].replace(
            edit.search,
            edit.replace,
            1,
        )

    for target, updated in contents.items():
        target.write_text(updated, encoding="utf-8")

    return AppliedPatch(
        files_modified=len(contents),
        edits_applied=len(plan.edits),
    )
