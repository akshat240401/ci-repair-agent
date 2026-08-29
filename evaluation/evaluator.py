from __future__ import annotations
import argparse
from pathlib import Path
from evaluation.case_loader import load_cases
from evaluation.result_schema import BenchmarkInspectionSummary, CaseInspectionResult
from evaluation.runner import run_full_suite, run_targeted_test
PROJECT_ROOT=Path(__file__).resolve().parents[1]
RESULTS_DIR=PROJECT_ROOT/"results"/"inspection"
def inspect_benchmark(*,case_id:str|None=None,timeout_seconds:int=30)->BenchmarkInspectionSummary:
    cases=load_cases()
    if case_id is not None:
        cases=[c for c in cases if c.case_id==case_id]
        if not cases: raise KeyError(f"Unknown benchmark case: {case_id}")
    results=[]
    for case in cases:
        targeted=run_targeted_test(case.repo_dir,case.metadata.targeted_test,timeout_seconds=timeout_seconds)
        full_suite=run_full_suite(case.repo_dir,timeout_seconds=timeout_seconds)
        results.append(CaseInspectionResult(case_id=case.case_id,targeted=targeted,full_suite=full_suite,targeted_failure_reproduced=(targeted.status=="FAIL"),full_suite_has_failure=(full_suite.status=="FAIL")))
    reproduced=sum(r.targeted_failure_reproduced for r in results); full_failed=sum(r.full_suite_has_failure for r in results)
    return BenchmarkInspectionSummary(total_cases=len(results),targeted_failures_reproduced=reproduced,full_suites_with_failure=full_failed,all_targeted_failures_reproduced=(len(results)>0 and reproduced==len(results)),cases=results)
def save_summary(summary:BenchmarkInspectionSummary)->Path:
    RESULTS_DIR.mkdir(parents=True,exist_ok=True); path=RESULTS_DIR/"benchmark_inspection.json"; path.write_text(summary.model_dump_json(indent=2),encoding="utf-8"); return path
def print_summary(summary:BenchmarkInspectionSummary,output_path:Path)->None:
    print("="*60); print("BENCHMARK INSPECTION"); print("="*60)
    print(f"Cases:                         {summary.total_cases}")
    print(f"Targeted failures reproduced: {summary.targeted_failures_reproduced}/{summary.total_cases}")
    print(f"Full suites with failure:      {summary.full_suites_with_failure}/{summary.total_cases}")
    print(f"All targeted failures valid:   {summary.all_targeted_failures_reproduced}")
    print(f"Results: {output_path}"); print("="*60)
def build_parser()->argparse.ArgumentParser:
    parser=argparse.ArgumentParser(description="Deterministic benchmark inspection harness.")
    parser.add_argument("--mode",choices=["inspect"],default="inspect",help="Only 'inspect' exists in this foundation block. Baseline/advanced modes come later.")
    parser.add_argument("--case",dest="case_id",default=None,help="Optional single benchmark case, e.g. case_003.")
    parser.add_argument("--timeout",type=int,default=30,help="Per pytest command timeout in seconds.")
    return parser
def main()->None:
    args=build_parser().parse_args(); summary=inspect_benchmark(case_id=args.case_id,timeout_seconds=args.timeout); path=save_summary(summary); print_summary(summary,path)
    if not summary.all_targeted_failures_reproduced: raise SystemExit(1)
if __name__=="__main__": main()
