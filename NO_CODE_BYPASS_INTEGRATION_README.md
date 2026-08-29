# No-code bypass integration check

This block adds a result-builder for the deterministic
`NO_CODE_PATCH_REQUIRED` path and a schema-level integration test.

Run:

```powershell
pytest -q tests
```

If the test fails because `RepairCaseResult.final_status` does not currently
allow `NO_CODE_PATCH_REQUIRED`, stop and share the failure. Do not commit.
