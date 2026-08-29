from evaluation.result_schema import CommandResult
from src.state.failure_signature import failure_signature

def test_same_failure_evidence_has_same_signature():
    a = CommandResult(
        kind="full", command=["pytest"], exit_code=1, status="FAIL",
        duration_seconds=0.1,
        stdout="FAILED tests/test_x.py::test_x\nE assert 1 == 2\n", stderr=""
    )
    b = CommandResult(
        kind="full", command=["pytest"], exit_code=1, status="FAIL",
        duration_seconds=9.0,
        stdout="FAILED tests/test_x.py::test_x\nE assert 1 == 2\n", stderr=""
    )
    assert failure_signature(a) == failure_signature(b)
