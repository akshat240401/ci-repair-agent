from src.users import get_user_name

def test_known_user(): assert get_user_name(1)=="Ada"
def test_missing_user_returns_none(): assert get_user_name(999) is None
