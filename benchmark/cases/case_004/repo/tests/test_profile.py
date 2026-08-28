from src.profile import serialize_profile

def test_profile_uses_display_name():
    r={"id":7,"username":"araval","display_name":"A. Raval"}
    assert serialize_profile(r)=={"id":7,"name":"A. Raval"}
