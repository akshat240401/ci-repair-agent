from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path
from src.schemas.benchmark import BenchmarkMetadata
PROJECT_ROOT = Path(__file__).resolve().parents[1]
CASES_DIR = PROJECT_ROOT / "benchmark" / "cases"
@dataclass(frozen=True)
class BenchmarkCase:
    case_id: str
    case_dir: Path
    repo_dir: Path
    log_path: Path
    metadata_path: Path
    metadata: BenchmarkMetadata
def load_case(case_dir: Path) -> BenchmarkCase:
    metadata_path = case_dir / "metadata.json"
    repo_dir = case_dir / "repo"
    log_path = case_dir / "failing_log.txt"
    if not metadata_path.exists(): raise FileNotFoundError(f"Missing metadata: {metadata_path}")
    if not repo_dir.is_dir(): raise FileNotFoundError(f"Missing repo directory: {repo_dir}")
    if not log_path.exists(): raise FileNotFoundError(f"Missing failing log: {log_path}")
    raw = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata = BenchmarkMetadata.model_validate(raw)
    if metadata.case_id != case_dir.name:
        raise ValueError(f"Case directory {case_dir.name!r} does not match metadata case_id {metadata.case_id!r}")
    targeted_test_file = metadata.targeted_test.split("::", 1)[0]
    if not (repo_dir / targeted_test_file).exists():
        raise FileNotFoundError(f"{metadata.case_id}: targeted test file does not exist: {targeted_test_file}")
    return BenchmarkCase(metadata.case_id, case_dir, repo_dir, log_path, metadata_path, metadata)
def load_cases() -> list[BenchmarkCase]:
    if not CASES_DIR.exists(): raise FileNotFoundError(f"Benchmark cases directory not found: {CASES_DIR}")
    case_dirs = sorted(p for p in CASES_DIR.iterdir() if p.is_dir() and p.name.startswith("case_"))
    if not case_dirs: raise RuntimeError("No benchmark cases found.")
    cases=[load_case(p) for p in case_dirs]
    ids=[c.case_id for c in cases]
    if len(ids)!=len(set(ids)): raise ValueError("Duplicate benchmark case IDs detected.")
    return cases
def get_case(case_id: str) -> BenchmarkCase:
    for case in load_cases():
        if case.case_id == case_id: return case
    raise KeyError(f"Unknown benchmark case: {case_id}")
