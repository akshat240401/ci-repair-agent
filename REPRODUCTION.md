# Reproduction Guide

This project targets **Python 3.11** on a clean checkout.

## 1. Clone

```powershell
git clone https://github.com/akshat240401/ci-repair-agent.git
cd ci-repair-agent
git checkout feat/evaluation-harness
```

For the final submission, replace the feature branch with the frozen release tag.

## 2. Create a clean Python environment

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .
pip install -r requirements-dev.txt
```

## 3. Deterministic validation

No model API call is required.

```powershell
pytest -q tests
python -m evaluation.evaluator --mode inspect
python -m evaluation.evidence_report
python -m evaluation.submission_cost_report
python -m evaluation.export_trajectories
```

Expected benchmark inspection:

- 20 benchmark cases
- targeted failures reproduced: 20/20
- full suites with failure: 20/20
- all targeted failures valid: True

## 4. Model configuration

```powershell
$env:OPENAI_API_KEY="YOUR_KEY"
$env:MODEL_NAME="gpt-5.6-luna"
$env:MODEL_REASONING_EFFORT="low"
```

Never commit API keys.

## 5. API-backed smoke test

```powershell
python -m evaluation.repair_loop_experiment --case case_010
Get-Content .\results\experiments\repair_loop\summary.json
```

A successful smoke run must contain:

```text
"cases": 1
"verified_repair_rate": 1.0
"unresolved_cases": []
```

Because model behavior can vary, an unresolved smoke run is a real failure signal
and must not be reported as a passed clean-room check.

## 6. Automated clean-room check

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\clean_room_check.ps1
```

With API smoke:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\clean_room_check.ps1 -RunApiSmoke
```

The script fails immediately when an external command returns a non-zero exit code.
For the API-backed variant, it also validates the generated repair summary and fails
unless the smoke case reaches a 100% one-case VRR.

## 7. Full advanced benchmark

```powershell
python -m evaluation.repair_loop_experiment
Get-Content .\results\experiments\repair_loop\summary.json
```

## Final submission rule

The final benchmark must be regenerated from the exact frozen/tagged `main`
commit. Development-branch numbers must not be presented as frozen submission
results.
