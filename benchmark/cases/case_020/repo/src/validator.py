ALLOWED_ISSUERS = {"internal", "partner"}
def validate_issuer(value):
    if value not in ALLOWED_ISSUERS:
        raise ValueError("untrusted issuer")
    return value
