from src.config_parser import parse_line

def test_hash_inside_quotes_is_preserved():
    assert parse_line('callback="https://example.com/#done"') == (
        "callback",
        "https://example.com/#done",
    )

def test_trailing_comment_is_removed():
    assert parse_line('mode="safe" # deployment default') == ("mode", "safe")

def test_full_line_comment_is_ignored():
    assert parse_line("# comment only") is None
