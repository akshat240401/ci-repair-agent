# Benchmark Expansion Block

Adds cases `case_006` through `case_012`.

After extraction run:

```powershell
python scripts/generate_failing_logs.py
python -m evaluation.validate_benchmark
python -m evaluation.evaluator --mode inspect
pytest -q tests
python -m evaluation.baseline_runner
```

Expected benchmark size: **12 cases**.
