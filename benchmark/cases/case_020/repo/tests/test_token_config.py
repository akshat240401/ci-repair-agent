import pytest
from src.auth import configured_issuer
from src.validator import validate_issuer

def test_missing_issuer_uses_default(monkeypatch):
    monkeypatch.delenv("TOKEN_ISSUER", raising=False)
    assert configured_issuer() == "ci-repair"

def test_default_issuer_is_valid():
    assert validate_issuer("ci-repair") == "ci-repair"

def test_unknown_issuer_is_rejected():
    with pytest.raises(ValueError):
        validate_issuer("evil")
