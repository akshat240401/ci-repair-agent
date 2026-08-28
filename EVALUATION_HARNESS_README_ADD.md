# Evaluation Harness Block — What Was Added

This block adds deterministic benchmark inspection before any LLM baseline exists.

## Commands

```powershell
python -m evaluation.evaluator --mode inspect
```

Optional single case:

```powershell
python -m evaluation.evaluator --mode inspect --case case_003
```

The command loads benchmark metadata, runs each targeted failing test and full pytest suite, captures exit codes/output/runtime, writes `results/inspection/benchmark_inspection.json`, and exits non-zero if a targeted failure cannot be reproduced.

**Do not run `--mode baseline` yet.** The baseline agent is the next milestone.
