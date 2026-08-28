from src.api import render_user
from src.consumer import greeting

def test_payload_uses_display_name_contract():
    payload, message = render_user({"id": 7, "name": "Ada"})
    assert payload == {"id": 7, "display_name": "Ada"}
    assert message == "Hello Ada"

def test_consumer_accepts_new_contract_directly():
    assert greeting({"display_name": "Grace"}) == "Hello Grace"
