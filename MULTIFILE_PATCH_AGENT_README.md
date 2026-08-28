# Steps 16-20: Multi-file Patch Agent

This block adds:
- patch-plan schema;
- multi-edit Search-and-Replace patch agent;
- transactional multi-file patch application;
- basic Git changed-file / diff context helpers;
- patch-agent experiment runner.

Run:

```powershell
pytest -q tests
python -m evaluation.patch_agent_experiment --case case_013
python -m evaluation.patch_agent_experiment --case case_015
```

If both complete, run:

```powershell
python -m evaluation.patch_agent_experiment
Get-Content .\results\experiments\patch_agent\summary.json
```

Do not commit until results are reviewed.
