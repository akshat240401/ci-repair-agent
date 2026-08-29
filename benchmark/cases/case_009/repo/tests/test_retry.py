from src.retry import call_with_retries

def test_two_retries_allows_three_total_attempts():
    calls = {"count": 0}

    def flaky():
        calls["count"] += 1
        if calls["count"] < 3:
            raise RuntimeError("temporary")
        return "ok"

    assert call_with_retries(flaky, 2) == "ok"
    assert calls["count"] == 3

def test_success_does_not_consume_extra_attempts():
    calls = {"count": 0}

    def ok():
        calls["count"] += 1
        return "ok"

    assert call_with_retries(ok, 4) == "ok"
    assert calls["count"] == 1
