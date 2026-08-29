# Steps 11-12: Triage Agent + Measurement

Run deterministic tests:

```powershell
pytest -q tests
```

Smoke test:

```powershell
python -m evaluation.triage_experiment --case case_013
```

Full 20-case experiment:

```powershell
python -m evaluation.triage_experiment
```

Inspect:

```powershell
Get-Content .\results\experiments\triage\summary.json
```

Do not change the benchmark, baseline prompt, model, or reasoning effort during
this experiment.
