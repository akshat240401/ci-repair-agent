# Hard Benchmark Expansion

Adds case_013 through case_020, bringing the benchmark to 20 cases.
Several cases require coordinated multi-file repairs, which the simple
one-shot baseline cannot express.

Run:

```powershell
python scripts/generate_failing_logs.py
python -m evaluation.validate_benchmark
python -m evaluation.evaluator --mode inspect
pytest -q tests
python -m evaluation.quality_gate --runs 3
```
