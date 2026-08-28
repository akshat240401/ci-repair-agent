from src.headers import get_header, normalized_headers

def test_lookup_accepts_lowercase_request():
    assert get_header({"Content-Type": "application/json"}, "content-type") == "application/json"

def test_lookup_accepts_mixed_case_storage():
    assert get_header({"x-request-id": "abc"}, "X-Request-Id") == "abc"

def test_normalized_headers_preserves_original_keys():
    headers = {"Content-Type": "application/json"}
    assert normalized_headers(headers) == headers
