from src.preprocessing.log_preprocessor import preprocess_log


def test_removes_ansi_and_duplicate_noise():
    raw = (
        "\x1b[31mFAILED\x1b[0m\n"
        "==========\n"
        "==========\n"
        "\n"
        "\n"
        "AssertionError: expected 1\n"
        "AssertionError: expected 1\n"
    )

    processed = preprocess_log(raw)

    assert "\x1b[" not in processed
    assert processed.count("==========") == 1
    assert processed.count("AssertionError: expected 1") == 1


def test_keeps_failure_evidence():
    raw = (
        "tests/test_x.py:10: AssertionError\n"
        "E assert 2 == 3\n"
        "FAILED tests/test_x.py::test_x\n"
    )

    processed = preprocess_log(raw)

    assert "tests/test_x.py:10: AssertionError" in processed
    assert "E assert 2 == 3" in processed
    assert "FAILED tests/test_x.py::test_x" in processed
