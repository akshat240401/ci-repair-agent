from src.state.loop_detector import LoopDetector

def test_duplicate_patch_detected():
    d = LoopDetector()
    assert d.record_patch("abc") is False
    assert d.record_patch("abc") is True

def test_repeated_repo_state_detected():
    d = LoopDetector()
    assert d.record_repo_state("x") is False
    assert d.record_repo_state("x") is True

def test_repeated_failure_detected():
    d = LoopDetector()
    assert d.record_failure("sig") is False
    assert d.record_failure("sig") is True

def test_two_state_oscillation_detected():
    d = LoopDetector()
    d.record_failure("A"); d.record_failure("B"); d.record_failure("A")
    assert d.has_two_state_oscillation() is True
