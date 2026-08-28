from src.cart import discounted_total

def test_total_is_correct(): assert discounted_total([30.0,10.0,20.0],0.10)==54.0
def test_total_does_not_mutate_cart():
    prices=[30.0,10.0,20.0]; original=list(prices); discounted_total(prices,0.10); assert prices==original
