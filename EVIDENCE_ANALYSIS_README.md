# Steps 28-31: Evidence Analysis

This block turns existing experiment outputs into:
- keep/remove decisions;
- hard-case evaluation;
- failure-mode analysis;
- project hot take;
- baseline-to-final headline improvement.

Run:

```powershell
pytest -q tests
python -m evaluation.evidence_report
Get-Content .\results\final_evidence\EVIDENCE_SUMMARY.md
```

No API call is required.
