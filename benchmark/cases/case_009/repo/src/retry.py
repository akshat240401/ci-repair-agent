def call_with_retries(operation, max_retries):
    last_error = None
    for _ in range(max_retries):
        try:
            return operation()
        except RuntimeError as exc:
            last_error = exc
    raise last_error
