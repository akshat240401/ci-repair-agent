from src.permissions import merge_permissions

def test_first_source_wins_and_order_is_preserved():
    assert merge_permissions(["read", "write"], ["read", "audit"]) == ["read", "write", "audit"]

def test_no_duplicates():
    assert merge_permissions(["read"], ["read", "read"]) == ["read"]
