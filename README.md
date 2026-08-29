# Agentic CI Failure Investigator & Verified Repair System

An agentic workflow for diagnosing failed Python CI runs, proposing minimal repairs, and proving those repairs with deterministic verification.

> **Current development result:** repeated baseline mean VRR **88.3%** vs current advanced development run **100.0%** on the same 20-case synthetic benchmark (**+11.7 percentage points**). Final submission numbers will be regenerated from the frozen/tagged `main` commit.

## Problem & user value

### Who has this problem?

Software engineers maintaining Python repositories with failing CI pipelines.

### What is the bottleneck?

A CI failure often leaves the engineer with fragmented evidence:

- a failing pytest log;
- repository code spread across multiple files;
- configuration and contract dependencies;
- a targeted failure that may hide a broader regression;
- uncertainty about whether a proposed patch truly fixed the system.

The expensive part is not typing a patch. It is **finding the root cause, changing the correct scope, and proving the repair did not introduce another failure**.

### What does this project do?

The system turns:

```text
repository + failing CI/test log + optional repository context
```

into one of:

```text
VERIFIED_REPAIR
NO_CODE_PATCH_REQUIRED
UNRESOLVED
```

A code repair counts as verified only when:

1. the patch applies safely;
2. Python syntax validation passes;
3. the targeted failing test passes;
4. the full regression suite passes.

## Primary metric

The primary metric is **Verified Repair Rate (VRR)**:

```text
verified repairable cases / total repairable cases
```

A repair is not counted merely because an LLM says it is correct.

## Current measured development result

| Metric | Simple baseline | Advanced system |
|---|---:|---:|
| Benchmark cases | 20 | 20 |
| Verified Repair Rate | 88.3% mean over 3 runs | 100.0% current development run |
| Baseline range | 85.0%-90.0% | - |
| Absolute improvement | - | +11.7 pp |
| Approx. API cost | $0.006661 mean/run | $0.048746 current run |

The baseline and advanced system use the same benchmark cases. Cost figures are evaluator estimates rather than billing statements.

The advanced result above is a **development result**, not the final frozen submission number.

## Why agents?

The project deliberately separates tasks that benefit from model judgment from tasks that require deterministic mechanics.

### Agent responsibilities

**Triage agent**
- classifies the failure;
- identifies evidence and likely target files;
- routes the next step.

**Investigation agent**
- uses bounded repository tools;
- searches code, symbols, tests, and configuration;
- identifies root cause and repair scope.

**Patch agent**
- proposes minimal exact Search-and-Replace edits;
- can express coherent multi-file repairs.

**Retry agent**
- receives deterministic verification feedback after a failed attempt;
- proposes a new complete repair plan;
- runs within a maximum three-attempt loop.

### Deterministic responsibilities

Code, not the LLM, handles:

- exact patch application;
- transactionality across multiple edits;
- syntax checking;
- targeted pytest verification;
- full regression verification;
- repository-state hashing;
- patch hashing;
- duplicate-state detection;
- no-progress detection;
- A -> B -> A oscillation detection;
- final status assignment.

**Design principle:** agents handle judgment; deterministic code handles mechanics and proof.

## Architecture

```text
Failing CI case
      |
      v
+-------------+
| Triage      |
| Agent       |
+-------------+
      |
      v
+-------------+      bounded tools
| Investigation| <-------------------+
| Agent        |                      |
+-------------+                       |
      |                               |
      v                               |
+-------------+                       |
| Patch Agent |                       |
+-------------+                       |
      |                               |
      v                               |
Transactional exact Search/Replace    |
      |                               |
      v                               |
+-------------------------------+     |
| Deterministic Verification    |     |
| 1. syntax                     |     |
| 2. targeted test              |     |
| 3. full regression suite      |     |
+-------------------------------+     |
      |                               |
 success|failure                       |
      |      \                         |
      v       \ verification feedback |
 VERIFIED     +--> Retry Agent --------+
 REPAIR
```

The retry loop is capped at three attempts and guarded by state/patch/failure-signature circuit breakers.

## Benchmark

The benchmark contains **20 deliberately broken synthetic Python repositories**.

It includes:

- local logic defects;
- boundary/None handling;
- configuration fallback issues;
- mapping errors;
- state mutation bugs;
- boolean parsing;
- semantic-version comparison;
- cache-key defects;
- retry semantics;
- regression-sensitive parsing;
- path handling;
- configuration precedence;
- multi-file API contract changes;
- case-insensitive lookup;
- unit migration across files;
- stale-cache behavior;
- path-containment bugs;
- ordering/deduplication defects;
- timestamp contract issues;
- configuration/validation drift.

The benchmark ground truth lives outside the agent-visible repository copies.

## Important failure modes we found

### 1. Single-file repair was not enough

Cross-file contract cases exposed the main limitation of the simple baseline. The decisive improvement was **multi-file transactional patch planning**.

### 2. A targeted test passing is not proof

A repair can satisfy the originally failing test and still break another test. Therefore the final gate always runs the full suite.

### 3. More preprocessing was not automatically better

We tested log preprocessing expecting cleaner context to improve repair quality. Repeated evaluation showed **0.0 percentage-point improvement** over the baseline.

We kept that negative result in the project history instead of presenting it as a success.

### 4. LLM output needs deterministic boundaries

Structured schemas, exact edits, state hashes, retry limits, and circuit breakers turned model proposals into a bounded engineering workflow.

## Hot take

**The strongest reliability improvement did not come from adding more prompting. It came from separating judgment from proof.**

Agents are useful for deciding what evidence matters and what repair is plausible. They should not be trusted to decide whether their own repair succeeded. The system became substantially more reliable when deterministic code controlled patch application, verification, and stopping conditions.

## Quick start

Requirements:

- Python **3.11**
- Git
- OpenAI API key only for model-backed runs

```powershell
git clone https://github.com/akshat240401/ci-repair-agent.git
cd ci-repair-agent

py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -e .
pip install -r requirements-dev.txt
```

Run the deterministic evaluation:

```powershell
python .\evaluate.py
```

Run one API-backed smoke case:

```powershell
$env:OPENAI_API_KEY="YOUR_KEY"
$env:MODEL_NAME="gpt-5.6-luna"
$env:MODEL_REASONING_EFFORT="low"

python .\evaluate.py --mode smoke --case case_010
```

Run the full advanced benchmark:

```powershell
python .\evaluate.py --mode full
```

For exact baseline reproduction, clean-room setup, expected outputs, and final freeze rules, see [REPRODUCTION.md](REPRODUCTION.md).

## Improvement changelog

The full experiment history is in [IMPROVEMENT_CHANGELOG.md](IMPROVEMENT_CHANGELOG.md).

It includes:

- the simple baseline;
- log preprocessing and why it was rejected as a primary improvement;
- triage;
- bounded investigation;
- multi-file transactional patching;
- deterministic verification;
- retry and circuit-breaker hardening.

## Trajectories

Representative artifacts are stored under `trajectories/`.

They include:

- simple repair;
- multi-file repair;
- regression-sensitive repair;
- configuration-contract repair;
- deterministic retry-recovery proof;
- deterministic circuit-breaker proof;
- deterministic `NO_CODE_PATCH_REQUIRED` policy proof.

Live benchmark trajectories and deterministic proof artifacts are explicitly labeled separately.

## Repository structure

```text
baseline/                 simple one-shot comparison agent
benchmark/                20 synthetic CI failure cases + evaluator-only ground truth
evaluation/               baseline/final runners, metrics, reports, experiments
results/                  measured experiment artifacts
scripts/                  setup/reproduction utilities
src/
  agents/                 triage, investigation, patch, retry agents
  orchestration/          no-code policy/result handling
  patching/               exact and transactional patch application
  schemas/                structured model outputs
  state/                  hashing and circuit-breaker logic
  tools/                  bounded repository investigation tools
  verification/           syntax/targeted/full-suite verification
tests/                    deterministic tests
trajectories/             representative agent/proof artifacts
evaluate.py               one-command evaluation entry point
IMPROVEMENT_CHANGELOG.md  measured development history
REPRODUCTION.md           clean-room reproduction instructions
```

## Safety and scope

- Python 3.11 / pytest benchmark repositories only.
- Repairs are applied to temporary/sandbox copies.
- Ground truth is evaluator-only.
- Credentials are supplied via environment variables and must not be committed.
- The system does not directly push repaired code to production repositories.
- `NO_CODE_PATCH_REQUIRED` is intentionally narrow and used only when triage identifies an environment/configuration problem with no repository target files.

## Reproducibility status

A separate clean checkout and clean Python 3.11 virtual environment has successfully reproduced:

- the deterministic test suite;
- 20/20 benchmark failure reproduction;
- evidence generation;
- fair baseline cost reporting;
- trajectory export;
- an API-backed verified-repair smoke case.

The final benchmark will be rerun only after the finished project is merged to `main` and the exact submission commit is tagged.
