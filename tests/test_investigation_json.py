from src.agents.investigation_agent import _extract_json


def test_extract_json_accepts_one_object():
    assert _extract_json('{"action":"final","x":1}') == {
        "action": "final",
        "x": 1,
    }


def test_extract_json_uses_first_object_if_model_duplicates_output():
    text = (
        '{"action":"tool","tool":"search_text"}'
        '{"action":"tool","tool":"search_text"}'
    )
    assert _extract_json(text) == {
        "action": "tool",
        "tool": "search_text",
    }
