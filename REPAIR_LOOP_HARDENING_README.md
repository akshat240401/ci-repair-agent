# Steps 21-27

Adds deterministic verification hardening, retry feedback, repo-state hashing,
patch hashing, failure signatures, duplicate-patch detection, no-progress
detection, oscillation detection, and a maximum of three repair attempts.

Run:

```powershell
pytest -q tests
python -m evaluation.repair_loop_experiment --case case_010
python -m evaluation.repair_loop_experiment
Get-Content .\results\experiments\repair_loop\summary.json
```
