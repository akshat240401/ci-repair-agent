# Baseline Agent Block

## What this adds
- OpenAI Responses API client.
- One simple, no-tools baseline repair agent.
- Full small-repository context supplied in one prompt.
- Exact Search-and-Replace patch proposal.
- Deterministic patch application.
- Python syntax validation.
- Targeted pytest verification.
- Full pytest regression verification.
- Baseline result JSON and Verified Repair Rate.

## Run deterministic tests first

```powershell
python -m pip install -e ".[dev]"
pytest -q tests
```

## Configure API key for the current PowerShell session

```powershell
$env:OPENAI_API_KEY="YOUR_KEY"
$env:MODEL_NAME="gpt-5.6-luna"
$env:MODEL_REASONING_EFFORT="low"
```

Do not commit the API key.

## Smoke test one case

```powershell
python -m evaluation.baseline_runner --case case_001
```

## Run all five starter cases

```powershell
python -m evaluation.baseline_runner
```

Results are written to:

```text
results/baseline/results.json
results/baseline/summary.json
```
