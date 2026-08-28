from src.auth import token_expiry_seconds

def test_default_token_ttl(): assert token_expiry_seconds()==3600
