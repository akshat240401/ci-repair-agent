def validate_timeout(config):
    timeout = config["timeout_ms"]
    if not 1 <= timeout <= 120:
        raise ValueError("timeout out of range")
    return True
