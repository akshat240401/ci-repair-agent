from src.events import normalize_timestamp
from src.parser import parse_timestamp

def test_round_trip_uses_z_suffix():
    assert normalize_timestamp("2026-08-28T12:00:00Z") == "2026-08-28T12:00:00Z"

def test_parser_returns_utc_aware_datetime():
    dt = parse_timestamp("2026-08-28T12:00:00Z")
    assert dt.tzinfo is not None
    assert dt.utcoffset().total_seconds() == 0
