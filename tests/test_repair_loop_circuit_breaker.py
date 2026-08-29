from src.state.loop_detector import LoopDetector


def test_duplicate_patch_circuit_breaker():
    detector = LoopDetector()
    assert detector.record_patch("same-patch") is False
    assert detector.record_patch("same-patch") is True


def test_no_progress_circuit_breaker():
    detector = LoopDetector()
    assert detector.record_failure("same-failure") is False
    assert detector.record_failure("same-failure") is True


def test_oscillation_circuit_breaker():
    detector = LoopDetector()
    detector.record_failure("state-A")
    detector.record_failure("state-B")
    detector.record_failure("state-A")
    assert detector.has_two_state_oscillation() is True
