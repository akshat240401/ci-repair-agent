from src.flags import cache_enabled

def cache_mode():
    return "cached" if cache_enabled() else "fresh"
