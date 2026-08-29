# Steps 32-34

This block closes:

- Step 32: production-safe `.env.example`
- Step 33: one-command evaluation entry point
- Step 34: final repository-structure validation

Run:

```powershell
pytest -q tests
python .\evaluate.py
```

`python .\evaluate.py` is deterministic and does not make model API calls.

Optional API smoke:

```powershell
python .\evaluate.py --mode smoke --case case_010
```

Full 20-case API-backed evaluation:

```powershell
python .\evaluate.py --mode full
```

Do not commit until the deterministic entry point passes.
