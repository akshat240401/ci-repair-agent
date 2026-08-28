# Investigation hotfix

Fixes two issues discovered before the experiment:

1. `case_018` used raw set iteration and could occasionally pass depending on
   Python hash ordering. It now fails deterministically while preserving the
   same intended root cause: order-destroying deduplication.
2. Investigation JSON parsing now accepts the first valid JSON object when a
   model response accidentally duplicates the same object back-to-back.

Run:

```powershell
python scripts/generate_failing_logs.py
python -m evaluation.evaluator --mode inspect
pytest -q tests
python -m evaluation.investigation_experiment --case case_013
```
