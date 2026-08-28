# Investigation scope hotfix

The model used the semantically correct value `cross_file_contract`, while the
strict schema only accepted `single_file` or `multi_file`.

This hotfix keeps the canonical stored values strict but normalizes common
model aliases such as `cross_file_contract` to `multi_file`.

Run:

```powershell
pytest -q tests
python -m evaluation.investigation_experiment --case case_020
python -m evaluation.investigation_experiment
Get-Content .\results\experiments\investigation\summary.json
```
