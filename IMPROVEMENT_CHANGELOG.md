# Improvement Changelog

This changelog records the major experiments used to develop the CI repair agent.
The goal is to preserve both successful and unsuccessful experiments instead of
presenting only the final architecture.

## Baseline

A one-shot LLM baseline received the failing log and repository context and
returned one exact Search-and-Replace repair.

Repeated 20-case quality-gate result:

- Mean Verified Repair Rate: **88.3%**
- Range: **85.0%-90.0%**

This is the comparison baseline for measured improvement.

## Experiment: Log preprocessing

**Hypothesis:** Removing ANSI/noise from failing CI logs would improve repair quality.

**Result:** The repeated quality gate showed **88.3% mean VRR**, identical to the
baseline (**0.0 percentage-point improvement**).

**Decision:** **REMOVE_AS_PRIMARY_IMPROVEMENT.**

The code is intentionally retained as experiment evidence. It may still be useful
for context cleanup, but the measured data does not justify claiming it as a
performance improvement.

## Experiment: Structured triage

**Hypothesis:** Explicit failure classification and target-file routing would
improve repair quality.

**Measured result:**

- Triage accuracy: **75.0%**
- Repair VRR in the triage experiment: **85.0%**

**Decision:** **KEEP_AS_ROUTING_COMPONENT**, not as the primary measured win.

## Experiment: Bounded investigation tools

**Hypothesis:** Letting the model investigate through bounded code/test/config
tools would improve evidence quality before patching.

**Measured result:**

- Root-file hit rate: **100.0%**
- All-root-files-found rate: **85.0%**
- Mean tool calls: **2.20**

**Decision:** **KEEP.**

The experiment improved evidence quality, especially for cases whose fixes span
multiple files, even though the old single-edit repair stage still limited end-to-end VRR.

## Experiment: Multi-file transactional patch planning

**Hypothesis:** Some CI failures are contracts across multiple files and cannot be
reliably fixed by a one-edit baseline.

**Measured result:**

- **20/20 verified repairs**
- **100.0% VRR** in the current development experiment

**Decision:** **KEEP_PRIMARY_WIN.**

The patch layer uses exact Search-and-Replace edits and validates all edits before
writing, so a multi-file plan applies transactionally or fails cleanly.

## Experiment: Deterministic verification + retry loop

**Hypothesis:** A repair should only count when syntax, the targeted failing test,
and the full regression suite all pass. Failed attempts should feed deterministic
evidence back into a bounded retry loop.

**Current development result:**

- **100.0% VRR**
- Current 20-case live run required no retries
- Retry recovery is separately proven by a deterministic integration test
- Circuit breakers are separately proven by unit tests

**Decision:** **KEEP_FOR_SAFETY_AND_ROBUSTNESS.**

Implemented circuit breakers include duplicate patches, repeated repository states,
repeated failure/no-progress detection, A -> B -> A oscillation detection, and a
maximum of three attempts.

## Current measured headline

- Repeated baseline mean VRR: **88.3%**
- Current development final VRR: **100.0%**
- Absolute improvement: **+11.7 percentage points**

These are development numbers. The final submission numbers must be regenerated
from the frozen/tagged `main` commit before submission.
