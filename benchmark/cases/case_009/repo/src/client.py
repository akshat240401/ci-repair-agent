from src.retry import call_with_retries

def fetch_with_retry(fetcher, retries=2):
    return call_with_retries(fetcher, retries)
