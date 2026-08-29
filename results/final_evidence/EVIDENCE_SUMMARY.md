# Evidence Summary

## Headline result

- Benchmark: **20 synthetic Python CI repair cases**
- Repeated baseline mean VRR: **88.3%**
- Baseline range: **85.0%-90.0%**
- Final verified repair loop VRR: **100.0%**
- Absolute improvement: **11.7 percentage points**

## Keep / remove decisions

- **log_preprocessor - REMOVE_AS_PRIMARY_IMPROVEMENT**: Repeated quality gate showed 88.3% mean VRR versus 88.3% baseline (0.0 pp).
- **triage_agent - KEEP_AS_ROUTING_COMPONENT**: Triage classification accuracy was 75.0%, but repair VRR was 85.0%; useful for structured routing, not sufficient as a standalone repair improvement.
- **investigation_agent - KEEP**: Root-file hit rate reached 100.0% with 2.20 mean tool calls.
- **multi_file_patch_agent - KEEP_PRIMARY_WIN**: Verified Repair Rate reached 100.0% with 20/20 verified repairs.
- **verified_repair_loop - KEEP_FOR_SAFETY_AND_ROBUSTNESS**: Verified Repair Rate was 100.0%. Retry/circuit-breaker behavior is separately demonstrated by deterministic tests.

## Hard-case evaluation

- **case_003**: patch agent=VERIFIED_REPAIR, repair loop=VERIFIED_REPAIR, attempts=1
- **case_010**: patch agent=VERIFIED_REPAIR, repair loop=VERIFIED_REPAIR, attempts=1
- **case_013**: patch agent=VERIFIED_REPAIR, repair loop=VERIFIED_REPAIR, attempts=1
- **case_015**: patch agent=VERIFIED_REPAIR, repair loop=VERIFIED_REPAIR, attempts=1
- **case_020**: patch agent=VERIFIED_REPAIR, repair loop=VERIFIED_REPAIR, attempts=1

## Failure-mode analysis

- **one-shot single-file repair cannot express cross-file contracts** -> multi-file transactional patch planning (observed in: case_013, case_015)
- **targeted test can pass while regression suite fails** -> full-suite verification gate plus retry feedback path (observed in: case_010)
- **model vocabulary can violate strict schemas despite correct semantics** -> canonical schema normalization with deterministic fallback (observed in: case_020)
- **stochastic LLM runs can make apparent improvements misleading** -> repeated baseline/experiment runs before accepting a change (observed in: quality_gate)

## Hot take

The strongest reliability gains did not come from adding more prompting. They came from separating judgment from proof: agents investigate and propose, while deterministic code applies exact edits, runs syntax/targeted/regression checks, and stops loops. Multi-file transactional repair was the decisive capability.
