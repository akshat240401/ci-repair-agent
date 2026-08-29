from src.settings import resolve_settings

def test_environment_overrides_file_configuration():
    resolved = resolve_settings(
        {"port": 9000, "debug": False},
        {"port": 7000},
    )
    assert resolved["port"] == 7000

def test_file_overrides_defaults_when_environment_missing():
    resolved = resolve_settings({"host": "0.0.0.0"}, {})
    assert resolved["host"] == "0.0.0.0"

def test_defaults_survive_when_not_overridden():
    resolved = resolve_settings({}, {})
    assert resolved["port"] == 8000
