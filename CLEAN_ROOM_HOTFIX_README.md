# Clean-room hotfix

The previous clean-room output exposed two real issues:

1. `pytest` was not installed in the fresh environment.
2. PowerShell's `$ErrorActionPreference = "Stop"` does not automatically fail
   on non-zero exit codes from native executables, so the script incorrectly
   printed `CLEAN ROOM CHECK PASSED`.
3. The API smoke case ended `UNRESOLVED`, but the runner exited zero, so the
   script also failed to detect that semantic failure.

This block fixes all three.

After extraction:

```powershell
pytest -q tests
git add .
git commit -m "test: add strict clean-room reproduction checks"
git push
```

Then rerun from the pushed branch:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\clean_room_check.ps1
```

Only after deterministic clean-room passes, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\clean_room_check.ps1 -RunApiSmoke
```

The API smoke check is now strict and will fail if the repair remains unresolved.
