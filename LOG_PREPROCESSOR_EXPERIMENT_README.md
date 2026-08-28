# Steps 9–10: Log Preprocessor + Measurement

Run deterministic tests:

```powershell
pytest -q tests
```

Smoke-test the known baseline failure:

```powershell
python -m evaluation.preprocessor_experiment --case case_010
```

Then run all 12 cases:

```powershell
python -m evaluation.preprocessor_experiment
```

Outputs:

```text
results/experiments/log_preprocessor/results.json
results/experiments/log_preprocessor/summary.json
results/experiments/log_preprocessor/diagnostics.json
```

The diagnostics file records the full regression stdout/stderr when a proposed
patch passes the targeted test but fails the complete suite.
