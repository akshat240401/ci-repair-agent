# Benchmark freeze test update

This update changes the original starter tests from expecting 5 cases to expecting the frozen 12-case benchmark.

Run:

```powershell
pytest -q tests
python -m evaluation.evaluator --mode inspect
```
