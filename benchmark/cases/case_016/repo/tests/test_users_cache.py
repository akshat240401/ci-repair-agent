from src.users import clear_cache, get_user, update_user

def setup_function():
    clear_cache()

def test_update_is_visible_after_cached_read():
    assert get_user("u1")["name"] == "Ada"
    update_user("u1", {"name": "Grace"})
    assert get_user("u1")["name"] == "Grace"

def test_cached_result_is_defensive_copy():
    user = get_user("u1")
    user["name"] = "Changed locally"
    assert get_user("u1")["name"] != "Changed locally"
