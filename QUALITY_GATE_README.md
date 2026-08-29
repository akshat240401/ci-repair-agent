# Quality Gate

Runs the exact 12-case benchmark multiple times for:
- the frozen simple baseline;
- the log-preprocessor experiment.

Run:

```powershell
pytest -q tests
python -m evaluation.quality_gate --runs 3
Get-Content .\results\quality_gate\quality_gate_summary.json
```

Do not change prompts, model, benchmark cases, or reasoning effort during this run.
