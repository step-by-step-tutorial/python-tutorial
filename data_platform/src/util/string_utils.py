def should_not_be_none(obj, name: str):
    if obj is None:
        raise ValueError(f"Value of {name} should not be None")


def should_not_be_none_or_empty(obj: str, name: str):
    if obj is None or not obj.strip():
        raise ValueError(f"Value of {name} should not be None or empty")
