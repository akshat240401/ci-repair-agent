import json
from pathlib import Path
from src.schemas.benchmark import BenchmarkMetadata
ROOT=Path(__file__).resolve().parents[1]; CASES=ROOT/'benchmark'/'cases'; GT=ROOT/'benchmark'/'ground_truth'
def main():
    case_dirs=sorted(p for p in CASES.iterdir() if p.is_dir())
    if not case_dirs: raise RuntimeError('No benchmark cases found')
    seen=set()
    for c in case_dirs:
        for p in [c/'metadata.json', c/'repo', c/'failing_log.txt', GT/f'{c.name}.json']:
            if not p.exists(): raise FileNotFoundError(p)
        m=BenchmarkMetadata.model_validate(json.loads((c/'metadata.json').read_text()))
        if m.case_id!=c.name: raise ValueError(f'{c.name}: metadata mismatch')
        if m.case_id in seen: raise ValueError(f'duplicate {m.case_id}')
        seen.add(m.case_id)
        test_file=m.targeted_test.split('::',1)[0]
        if not (c/'repo'/test_file).exists(): raise FileNotFoundError(test_file)
        gt=json.loads((GT/f'{c.name}.json').read_text())
        if gt.get('case_id')!=c.name: raise ValueError(f'{c.name}: ground-truth mismatch')
    print(f'Validated {len(case_dirs)} benchmark cases successfully.')
if __name__=='__main__': main()
