# Improvement Changelog

## Stage 0 — Project and benchmark foundation

**Observed problem:** Agent performance cannot be compared credibly before scope, benchmark cases, success criteria, and reproduction steps are fixed.

**Hypothesis:** A Python-only benchmark will reduce toolchain variability and make later baseline-vs-advanced comparisons fair and reproducible.

**Change:** Restricted the benchmark to Python 3.11 + pytest; defined Verified Repair Rate; created five synthetic broken repositories; separated evaluator-only ground truth; added benchmark validation and failing-log generation.

**Evidence:** Stage-0 acceptance is structural: all five cases validate and deterministically reproduce a targeted failure.

**Decision:** KEPT.

**Next:** Build evaluator + fair one-agent baseline.
