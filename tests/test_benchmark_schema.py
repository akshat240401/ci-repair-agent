import json
from pathlib import Path
from src.schemas.benchmark import BenchmarkMetadata
ROOT = Path(__file__).resolve().parents[1]
EXPECTED_CASE_IDS = [f"case_{i:03d}" for i in range(1, 21)]

def test_all_metadata_validates():
    cases = sorted((ROOT / "benchmark" / "cases").glob("case_*"))
    assert [c.name for c in cases] == EXPECTED_CASE_IDS
    for case_dir in cases:
        data=json.loads((case_dir/"metadata.json").read_text(encoding="utf-8"))
        assert BenchmarkMetadata.model_validate(data).case_id == case_dir.name
