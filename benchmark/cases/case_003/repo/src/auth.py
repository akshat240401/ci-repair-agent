from src.settings import TOKEN_TTL
def token_expiry_seconds() -> int:
    return int(TOKEN_TTL)
