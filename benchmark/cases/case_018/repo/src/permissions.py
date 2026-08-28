def merge_permissions(primary, inherited):
    return list(set(primary + inherited))
