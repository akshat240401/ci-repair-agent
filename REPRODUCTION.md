# Reproduction Guide — Stage 0

## Requirements
- Python 3.11
- Git
- `uv` recommended, or standard `venv` + `pip`

## Setup
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd ci-repair-agent
uv venv --python 3.11
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Windows PowerShell activation:
```powershell
.venv\Scripts\Activate.ps1
```

## Validate benchmark
```bash
python -m evaluation.validate_benchmark
```
Expected: `Validated 5 benchmark cases successfully.`

## Re-generate real failing logs
```bash
python scripts/generate_failing_logs.py
```
Each case is intentionally broken; the script expects its targeted test to fail and stores real pytest output in `failing_log.txt`.

## Project tests
```bash
pytest -q tests
```

## One command
```bash
make check
```

## Data / cost
All benchmark code is synthetic. No private repo or personal data is needed. No LLM API call is made in this milestone, so API cost is $0.
