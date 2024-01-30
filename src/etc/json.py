def to_json(items):
    if items is None:
        return None
    if isinstance(items, list):
        return [item.to_json() for item in items]
    else:
        return items.to_json()