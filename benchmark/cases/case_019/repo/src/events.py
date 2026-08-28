from src.parser import parse_timestamp
from src.formatter import format_timestamp
def normalize_timestamp(value):
    return format_timestamp(parse_timestamp(value))
