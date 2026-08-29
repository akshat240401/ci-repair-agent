from src.config_parser import parse_line

def parse_config(text):
    result = {}
    for line in text.splitlines():
        parsed = parse_line(line)
        if parsed:
            key, value = parsed
            result[key] = value
    return result
