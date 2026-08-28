# Project Specification — Agentic CI Failure Investigator & Verified Repair System

## Problem
Software engineers lose time diagnosing Python CI failures because evidence is fragmented across logs, failing tests, source code, configuration, and recent changes.

## Intended user
A software engineer debugging a failed Python 3.11 / pytest CI run.

## Frozen scope
- Python 3.11 repositories only.
- pytest-based benchmark repositories.
- Local / sandbox execution only.
- No production deployment or production writes.
- No multi-language support.
- No heavy external infrastructure.
- Inputs: repository + failing CI/test log + optional Git diff / changed files.
- Outputs: failure classification + evidence-backed root cause + minimal repair + deterministic verification status.

## Legal final statuses
- `VERIFIED_REPAIR`
- `NO_CODE_PATCH_REQUIRED`
- `UNRESOLVED`

## Primary metric
**Verified Repair Rate (VRR)** = repairable cases where the edit applies successfully, Python syntax passes, the targeted failing test passes, and the complete existing pytest suite passes / total repairable benchmark cases.

## Engineering rule
**LLMs handle judgment; deterministic code handles mechanics and proof.**

This starter milestone implements only the project skeleton, benchmark schema, five synthetic broken repositories, benchmark validation, failing-log generation, and Git/GitHub setup. The baseline and advanced agents are intentionally not implemented yet.
