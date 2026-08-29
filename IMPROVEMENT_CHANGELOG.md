# Improvement Changelog

This document records the experiments that shaped the final CI repair workflow.

Every meaningful iteration is kept here, including changes that were later rejected. Development metrics are retained as historical evidence; the authoritative submission metrics are reported separately in the frozen final evaluation section below.

| Stage | What we tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Baseline | One direct agent sees the failing log and small repository and returns one exact Search-and-Replace edit. Establish a fair minimal starting point. | Repeated 20-case quality gate: **88.3% mean VRR**, **85.0%-90.0% range**. | Keep as the comparison baseline. |
| Log preprocessing | Strip ANSI/noise before the model sees the CI log. Hypothesis: cleaner context would improve repair accuracy. | Repeated mean VRR **88.3%**, identical to baseline: **0.0 pp improvement**. | **Removed as a primary improvement.** Retain code/evidence because the failed hypothesis is informative. |
| Structured triage | Explicitly classify failure type, evidence, likely target files, root cause, and next step. | **75.0%** triage classification accuracy; repair experiment **85.0% VRR**. | Keep as a routing/evidence component, not the main performance claim. |
| Bounded investigation tools | Let an investigation agent search code, symbols, tests, directories, and config instead of receiving unrestricted context. | Root-file hit rate **100.0%**; all-root-files-found rate **85.0%**; mean **2.20 tool calls**. Repair VRR remained constrained by the single-edit repair layer. | Keep. Better investigation alone did not solve multi-file repair. |
| Multi-file transactional patch plan | Replace the one-edit limitation with a structured plan containing up to six exact edits. Validate the entire plan before writing. | Current development experiment: **20/20 verified repairs**, **100.0% VRR**. Multi-file cases such as `case_013`, `case_015`, and `case_020` were repaired coherently. | **Keep as the primary measured engineering win.** |
| Deterministic verification | Require patch application, syntax, targeted test, and full regression suite before calling a repair successful. | Regression-sensitive cases demonstrated that targeted success alone is insufficient. Current development repair-loop run: **20/20 verified**. | Keep. The agent does not judge its own success. |
| Feedback retry | Feed failed verification evidence into a bounded retry agent. | Current live 20-case development run happened to succeed on attempt 1; deterministic integration testing forces a bad first patch and verifies recovery on attempt 2. | Keep for robustness; do not fabricate a live retry claim. |
| Circuit breakers | Add patch hashes, repository-state hashes, repeated-failure detection, oscillation detection, and a three-attempt maximum. | Deterministic tests prove duplicate patch, repeated state/no-progress, and A -> B -> A detection. | Keep. Reliability includes knowing when to stop. |
| No-code bypass | Add a narrow deterministic policy for environment/config failures with no repository target files. | Unit/schema integration tests produce `NO_CODE_PATCH_REQUIRED` with zero patch attempts; negative controls prevent use for normal code defects. | Keep as a bounded non-code path. |
| Clean-room reproduction | Clone into a separate temporary directory and install only declared dependencies. | First attempt exposed missing `pytest` and a PowerShell false-positive pass. After fixing both, fresh environment tests passed and an API-backed smoke case reached `VERIFIED_REPAIR`. | Keep strict clean-room script. Reproduction failures became testable evidence rather than documentation assumptions. |

## Current development headline

- Benchmark: **20 synthetic Python CI failure cases**
- Primary metric: **Verified Repair Rate (VRR)**
- Repeated baseline mean: **88.3%**
- Current advanced development run: **100.0%**
- Development delta: **+11.7 percentage points**

These values are retained as **development history only** and are not the final submission headline.

## What contributed most?

The largest practical capability change was **multi-file transactional patch planning combined with deterministic verification**.

The benchmark revealed that stronger reasoning alone was insufficient when the repair representation could express only one edit. Once the system could repair cross-file contracts atomically and prove the result with targeted plus full-suite tests, previously persistent failure modes became repairable.

## Removed experiment

**Log preprocessing is intentionally retained as a documented negative experiment.**

It sounded useful, but repeated testing showed no improvement over the baseline. That result changed the project direction: effort moved from cosmetic context cleanup toward investigation quality, repair expressiveness, and deterministic proof.

## Main failure mode

The most important failure mode was:

> **A plausible local patch can be wrong at repository scope.**

This appeared in two forms:

1. a failure contract spans multiple files; or
2. the targeted test passes while another regression test fails.

That is why the final workflow uses multi-file transactional edits and requires the full regression suite.

## Hot take

**Reliable agents need less authority over proof, not more intelligence about proof.**

Use the model where ambiguity exists: interpreting symptoms, choosing evidence, identifying the contract, and proposing a repair. Use deterministic software where correctness can be checked: applying edits, running tests, hashing state, enforcing limits, and declaring success.

The strongest improvement came from redesigning the boundary between those two responsibilities.


## Frozen final evaluation

The final repeated evaluation was run from `v1.0.0-hackathon` at commit `01231fd92db105b1fe8be18a4e4340fcd3dc5b5a` using the same 20 benchmark cases for both systems.

| Metric | Baseline | Advanced |
|---|---:|---:|
| Run 1 VRR | 80.0% | 100.0% |
| Run 2 VRR | 90.0% | 100.0% |
| Run 3 VRR | 90.0% | 100.0% |
| **Mean VRR** | **86.7%** | **100.0%** |
| VRR range | 80.0%-90.0% | 100.0%-100.0% |
| Population stddev | 4.71 pp | 0.00 pp |
| Mean estimated API cost/run | $0.007766 | $0.044514 |

**Final measured improvement: +13.3 percentage points.**

All six run artifacts and the aggregate report are stored under `results/frozen_final/`. Cost values are evaluator estimates rather than billing statements.
