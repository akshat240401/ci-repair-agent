# Investigation scope normalization — final fix

`recommended_change_scope` is now treated as derived metadata instead of fragile
model vocabulary.

Canonical stored values remain:
- `single_file`
- `multi_file`

Any recognizable alias is normalized. Unknown wording falls back to the number
of `target_files`, so vocabulary variation cannot abort the experiment.

Run:

```powershell
pytest -q tests
python -m evaluation.investigation_experiment --case case_020
```

If case_020 completes, run:

```powershell
python -m evaluation.investigation_experiment
Get-Content .\results\experiments\investigation\summary.json
```
