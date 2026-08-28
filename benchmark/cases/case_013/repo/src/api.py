from src.producer import build_user_payload
from src.consumer import greeting
def render_user(user):
    payload = build_user_payload(user)
    return payload, greeting(payload)
