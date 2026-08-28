from src.store import read_user, write_user
_CACHE = {}
def get_user(user_id):
    if user_id not in _CACHE:
        _CACHE[user_id] = read_user(user_id)
    return dict(_CACHE[user_id])
def update_user(user_id, data):
    write_user(user_id, data)
def clear_cache():
    _CACHE.clear()
