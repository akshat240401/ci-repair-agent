# Clean-room reproducibility block

After extracting, first run the normal repository tests:

```powershell
pytest -q tests
```

Then, from the repository root, run a completely separate clean checkout:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\clean_room_check.ps1
```

This deletes only the script's temporary clean-room directory under `%TEMP%`,
not the working repository.

Optional API-backed smoke test:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\clean_room_check.ps1 -RunApiSmoke
```

For the API-backed variant, `OPENAI_API_KEY`, `MODEL_NAME`, and
`MODEL_REASONING_EFFORT` should already be set in the parent shell.

Do not commit until the clean-room run passes.
