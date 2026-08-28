import json
from pathlib import Path
from src.schemas.benchmark import BenchmarkMetadata
ROOT=Path(__file__).resolve().parents[1]
def test_all_metadata_validates():
    cases=sorted((ROOT/'benchmark'/'cases').glob('case_*')); assert len(cases)==5
    for c in cases:
        m=BenchmarkMetadata.model_validate(json.loads((c/'metadata.json').read_text()))
        assert m.case_id==c.name and m.language=='python' and m.python_version=='3.11'
