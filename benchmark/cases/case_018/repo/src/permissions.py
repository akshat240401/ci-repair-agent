def merge_permissions(primary, inherited):
    return sorted(set(primary + inherited))
