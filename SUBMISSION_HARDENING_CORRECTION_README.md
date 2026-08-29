# Submission hardening correction

Fixes:
1. Fair baseline cost accounting: only the three 20-case quality-gate baseline runs are used.
2. Adds a narrow deterministic NO_CODE_PATCH_REQUIRED policy for environment/config failures with zero repository target files.
3. Exports a separately labeled config-only bypass proof trajectory.

Run:

```powershell
pytest -q tests
python -m evaluation.submission_cost_report
python -m evaluation.export_trajectories
Get-Content .\results\submission\cost_comparison.json
Get-Content .\trajectories\manifest.json
```

Do not commit until outputs are reviewed.
