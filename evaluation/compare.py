from __future__ import annotations
import json
from pathlib import Path
from evaluation.metrics import average_cost_usd, average_latency_seconds, unresolved_rate, verified_repair_rate
from evaluation.result_schema import RepairCaseResult
def load_repair_results(path:Path)->list[RepairCaseResult]:
    raw=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw,list): raise ValueError(f"Expected a JSON list in {path}")
    return [RepairCaseResult.model_validate(item) for item in raw]
def summarize(path:Path)->dict[str,float|int]:
    results=load_repair_results(path)
    return {"cases":len(results),"verified_repair_rate":verified_repair_rate(results),"unresolved_rate":unresolved_rate(results),"average_latency_seconds":average_latency_seconds(results),"average_cost_usd":average_cost_usd(results)}
def compare(baseline_path:Path,advanced_path:Path)->dict[str,object]:
    baseline=summarize(baseline_path); advanced=summarize(advanced_path)
    return {"baseline":baseline,"advanced":advanced,"verified_repair_rate_change_pp":(float(advanced["verified_repair_rate"])-float(baseline["verified_repair_rate"]))*100.0}
