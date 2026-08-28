import os

def cache_enabled():
    return bool(os.getenv("USE_CACHE", "false"))
