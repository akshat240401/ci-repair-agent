from src.settings import token_issuer
from src.validator import validate_issuer
def configured_issuer():
    return validate_issuer(token_issuer())
