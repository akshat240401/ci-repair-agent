# Submission hardening: cost reporting + trajectories

Run:

```powershell
pytest -q tests
python -m evaluation.submission_cost_report
python -m evaluation.export_trajectories
Get-Content .\results\submission\cost_comparison.json
Get-Content .\trajectories\manifest.json
```

Important:
- cost figures are approximate evaluator estimates, not billing statements;
- live benchmark trajectories and deterministic proof trajectories are labeled separately;
- no synthetic trajectory is presented as a live LLM run;
- final submission metrics must later be regenerated from the tagged main commit.
