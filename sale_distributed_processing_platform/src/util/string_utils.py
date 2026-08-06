def should_be_not_none(name: str, val):
    if val is None:
        raise ValueError(f"Value of {name} should not be None")


def should_be_not_none_or_empty(name: str, val: str):
    if val is None or not val.strip():
        raise ValueError(f"Value of {name} should not be None or empty")
