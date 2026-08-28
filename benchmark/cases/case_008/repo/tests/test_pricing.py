from src.pricing import clear_cache, get_price

def setup_function():
    clear_cache()

def test_cache_does_not_leak_price_between_regions():
    assert get_price("sku-1", "US") == 10
    assert get_price("sku-1", "EU") == 12

def test_cache_reuses_same_region_value():
    assert get_price("sku-2", "US") == 7
    assert get_price("sku-2", "US") == 7
