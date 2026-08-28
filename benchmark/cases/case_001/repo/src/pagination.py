def page_count(total_items: int, page_size: int) -> int:
    if page_size <= 0:
        raise ValueError("page_size must be positive")
    if total_items == 0:
        return 0
    return total_items // page_size + 1
