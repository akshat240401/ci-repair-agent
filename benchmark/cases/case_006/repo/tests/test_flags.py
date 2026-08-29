from src.flags import cache_enabled

def test_false_string_disables_cache(monkeypatch):
    monkeypatch.setenv("USE_CACHE", "false")
    assert cache_enabled() is False

def test_true_string_enables_cache(monkeypatch):
    monkeypatch.setenv("USE_CACHE", "true")
    assert cache_enabled() is True
