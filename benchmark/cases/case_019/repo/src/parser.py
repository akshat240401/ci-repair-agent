from datetime import datetime
def parse_timestamp(value):
    return datetime.fromisoformat(value)
