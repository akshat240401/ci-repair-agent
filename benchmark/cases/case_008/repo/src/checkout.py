from src.pricing import get_price

def checkout_price(product_id, region):
    return get_price(product_id, region)
