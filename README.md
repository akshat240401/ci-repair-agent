# Agentic CI Failure Investigator & Verified Repair System

Initial hackathon starter repository for a reproducible agentic workflow that diagnoses failed Python CI runs, collects targeted evidence, proposes minimal repairs, and verifies them deterministically.

## Current milestone
This package intentionally contains only the initial combined setup steps:
- frozen Python 3.11 / pytest scope;
- benchmark schema;
- 5 deliberately broken synthetic repositories;
- evaluator-only ground truth stored outside agent-visible repos;
- benchmark validator;
- failing-log generator;
- GitHub Actions + Git/GitHub setup guide.

No advanced agent is implemented yet. The benchmark/evaluator foundation comes first.

## Quick start — recommended (`uv`)
```bash
uv venv --python 3.11
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
uv pip install -e ".[dev]"
python -m evaluation.validate_benchmark
python scripts/generate_failing_logs.py
pytest -q tests
```

## Standard venv + pip
```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m evaluation.validate_benchmark
python scripts/generate_failing_logs.py
pytest -q tests
```

## Useful commands
```bash
make validate
make logs
make test
make check
```

## Starter cases
| Case | Failure family | Purpose |
|---|---|---|
| case_001 | off-by-one | simple local logic bug |
| case_002 | None handling | defensive / boundary behavior |
| case_003 | upstream config | challenging symptom-vs-root-cause case |
| case_004 | wrong mapping key | data transformation defect |
| case_005 | state mutation | side-effect defect |

## Next milestone
1. Build evaluation harness.
2. Build fair one-agent baseline.
3. Run/freeze baseline results.
4. Classify baseline failures.
5. Begin advanced iterations only after that.
