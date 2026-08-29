# Step 40 — Final End-to-End / Repository Audit

This audit is the last deterministic gate before merge, tagging, and frozen final evaluation.

It checks:

- no temporary patch-helper files remain;
- no committed OpenAI credential pattern is detected;
- evaluator ground truth is not referenced by agent-visible runtime code;
- smoke evaluations cannot overwrite canonical full-run evidence;
- the no-code path is wired into the actual repair-loop runner;
- all tests pass;
- all 20 broken benchmark cases reproduce their failures;
- evidence/cost reports regenerate;
- canonical advanced results contain 20 cases;
- README/changelog/reproduction docs contain submission-critical material;
- all seven representative trajectory artifacts are present.

This step intentionally does **not** make new model calls.

After it passes, run the strict clean-room check again. Then the project is ready for the merge/tag/frozen-evaluation sequence.
