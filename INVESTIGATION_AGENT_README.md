# Steps 13-15: Bounded Tools + Investigation Agent + Measurement

Run:

```powershell
pytest -q tests
```

Smoke-test the two-file contract case:

```powershell
python -m evaluation.investigation_experiment --case case_013
```

Then run all 20:

```powershell
python -m evaluation.investigation_experiment
```

Inspect:

```powershell
Get-Content .\results\experiments\investigation\summary.json
```

Do not commit until the experiment output has been reviewed.
