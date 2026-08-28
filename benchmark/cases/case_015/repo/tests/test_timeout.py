import pytest
from src.service import build_config
from src.validator import validate_timeout

def test_config_serializes_timeout_in_milliseconds():
    assert build_config(30) == {"timeout_ms": 30000}

def test_validator_accepts_millisecond_range():
    assert validate_timeout({"timeout_ms": 30000}) is True

def test_validator_rejects_more_than_two_minutes():
    with pytest.raises(ValueError):
        validate_timeout({"timeout_ms": 121000})
