# Reproduction Guide

This guide is written for someone starting from a clean environment.

## Scope and versions

- Python: **3.11**
- Test framework: **pytest 8.3.5**
- Package dependencies are declared in `pyproject.toml`
- Development test dependency is pinned in `requirements-dev.txt`
- API-backed agent runs require an OpenAI API key
- Model used during development: `gpt-5.6-luna`
- Development reasoning effort: `low`

Costs shown by the evaluator are approximate API estimates, not billing statements.

## 1. Clone

During development:

```powershell
git clone https://github.com/akshat240401/ci-repair-agent.git
cd ci-repair-agent
git checkout feat/evaluation-harness
```

For final judging, use the frozen release tag from tagged main instead of the feature branch.

## 2. Create a clean Python environment

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -e .
pip install -r requirements-dev.txt
```

## 3. Deterministic validation

No API call is required:

```powershell
python .\evaluate.py
```

Equivalent direct benchmark-inspection command:

```powershell
python -m evaluation.evaluator --mode inspect
```

This runs:

```text
pytest -q tests
benchmark inspection
evidence report generation
cost/token report generation
trajectory export
```

Expected benchmark inspection:

```text
Cases:                         20
Targeted failures reproduced: 20/20
Full suites with failure:      20/20
All targeted failures valid:   True
```

The exact unit-test count may increase before final submission; all tests must pass.

## 4. Configure model-backed runs

PowerShell:

```powershell
$env:OPENAI_API_KEY="YOUR_KEY"
$env:MODEL_NAME="gpt-5.6-luna"
$env:MODEL_REASONING_EFFORT="low"
```

Never place a real key in `.env.example`, source files, result files, or submitted trajectories.

## 5. Reproduce the simple baseline

### One baseline run on all 20 cases

```powershell
python -m evaluation.baseline_runner
```

Expected artifacts:

```text
results/baseline/results.json
results/baseline/summary.json
```

The terminal prints:

```text
Cases
Verified repairs
Verified Repair Rate
Input tokens
Output tokens
Estimated API cost
```

### Reproduce the repeated development baseline

The development baseline headline is based on three runs over the same 20 cases.

```powershell
python -m evaluation.quality_gate --runs 3
```

This runner evaluates both the baseline and the log-preprocessing experiment because that comparison was part of the development history.

Expected report:

```text
results/quality_gate/quality_gate_summary.json
```

Recorded development baseline:

```text
Mean VRR: 88.3%
Range:    85.0%-90.0%
```

Because model output is stochastic, an individual rerun may not produce identical per-run values. The final submission will freeze a repeated evaluation from the exact tagged commit.

## 6. Reproduce one advanced repair

```powershell
python .\evaluate.py --mode smoke --case case_010
```

A successful smoke run contains:

```text
VERIFIED_REPAIR
Verified Repair Rate: 100.0%
Unresolved: []
```

A model-backed smoke run that ends `UNRESOLVED` is a real failed run and must not be reported as a passed reproduction.

## 7. Run the full advanced benchmark

```powershell
python .\evaluate.py --mode full
```

Equivalent core runner:

```powershell
python -m evaluation.repair_loop_experiment
```

Expected artifacts:

```text
results/experiments/repair_loop/results.json
results/experiments/repair_loop/diagnostics.json
results/experiments/repair_loop/summary.json
```

Current development run:

```text
20 cases
20 verified repairs
100.0% VRR
```

This is not yet the frozen submission result.

## 8. Generate cost/token comparison

```powershell
python -m evaluation.submission_cost_report
Get-Content .\results\submission\cost_comparison.json
```

Development comparison currently uses exactly the three 20-case baseline quality-gate runs.

Recorded development estimates:

```text
Baseline mean input tokens:   12,664.0
Baseline mean output tokens:   3,440.3
Baseline mean estimated cost: $0.006661

Current advanced input tokens: 106,836
Current advanced output tokens: 22,816
Current advanced estimated cost: $0.048746
```

The additional cost buys investigation, structured multi-file planning, deterministic verification, and bounded retry behavior.

## 9. Export representative trajectories

```powershell
python -m evaluation.export_trajectories
Get-Content .\trajectories\manifest.json
```

The manifest distinguishes:

- recorded live benchmark diagnostics;
- deterministic retry proof;
- deterministic circuit-breaker proof;
- deterministic config-only bypass proof.

No deterministic proof artifact is presented as though it were a live LLM trajectory.

## 10. Automated clean-room reproduction

Run from the project root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\clean_room_check.ps1
```

This:

1. removes the previous dedicated temporary clean-room directory;
2. clones the repository again;
3. checks out the requested ref;
4. creates a fresh Python 3.11 virtual environment;
5. installs only declared dependencies;
6. runs tests;
7. validates the benchmark;
8. regenerates evidence/cost/trajectory artifacts;
9. fails on any non-zero native command exit code.

API-backed clean-room smoke:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\clean_room_check.ps1 -RunApiSmoke
```

The API-backed version additionally fails unless the smoke summary reports a one-case VRR of `1.0`.

## Approximate runtime

Observed on the development Windows machine:

- deterministic test suite: roughly **35-40 seconds**;
- benchmark inspection/report generation: additional seconds;
- one API smoke repair: typically on the order of seconds to tens of seconds depending on API latency;
- full 20-case model evaluation: dependent on network/API latency.

Do not interpret these as performance guarantees.

## Data

The benchmark is synthetic and included in the repository.

```text
benchmark/
```

Evaluator-only repair ground truth is separated under:

```text
benchmark/ground_truth/
```

It must never be supplied to agent prompts or bounded repository tools.

## Final freeze procedure

Development results are deliberately labeled as development results.

Before submission:

1. finish implementation and documentation;
2. pass the full repository audit;
3. merge the feature PR into `main`;
4. tag the exact submission commit;
5. perform a fresh checkout of that tag;
6. create a fresh Python 3.11 environment;
7. rerun the repeated baseline/final evaluation on the same 20 cases;
8. freeze the output artifacts;
9. update README headline numbers only from those frozen artifacts;
10. do not modify code after the tagged evaluation without invalidating and rerunning the results.

This ensures the submitted code and reported metrics refer to the same repository state.


For final submission, metrics are regenerated from tagged `main`.
