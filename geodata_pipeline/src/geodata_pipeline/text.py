import re

WHITESPACE_PATTERN = re.compile(r"\s+")


def normalize(value: str | None) -> str:
    """Lower-case a value and collapse whitespace so names can be compared."""
    if not value:
        return ""

    return WHITESPACE_PATTERN.sub(" ", value.strip().lower())
