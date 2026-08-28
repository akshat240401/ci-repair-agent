from src.headers import get_header
def content_type(headers):
    return get_header(headers, "Content-Type")
