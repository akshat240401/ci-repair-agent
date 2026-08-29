import os
DEFAULT_ISSUER = "ci-repair"
def token_issuer():
    return os.getenv("TOKEN_ISSUER")
