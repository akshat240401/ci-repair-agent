def discounted_total(prices: list[float], discount: float) -> float:
    if not 0 <= discount <= 1: raise ValueError("discount must be between 0 and 1")
    prices.sort()
    return sum(prices)*(1-discount)
