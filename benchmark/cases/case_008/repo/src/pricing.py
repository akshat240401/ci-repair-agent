PRICE_TABLE = {
    ("sku-1", "US"): 10,
    ("sku-1", "EU"): 12,
    ("sku-2", "US"): 7,
}

_CACHE = {}

def get_price(product_id, region):
    key = product_id
    if key not in _CACHE:
        _CACHE[key] = PRICE_TABLE[(product_id, region)]
    return _CACHE[key]

def clear_cache():
    _CACHE.clear()
