import re
import unicodedata

NON_LETTER_OR_DIGIT_PATTERN = re.compile(r"[^a-z0-9]+")
REPEATED_DOTS_PATTERN = re.compile(r"\.+")


def to_email_local_part(value: str) -> str:
    """Turn a name into an email local part: ASCII, lower case, words joined by dots ("Zoë O'Neill" -> "zoe.o.neill")."""
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    cleaned = NON_LETTER_OR_DIGIT_PATTERN.sub(".", ascii_value.lower().strip())
    cleaned = REPEATED_DOTS_PATTERN.sub(".", cleaned).strip(".")
    if not cleaned:
        raise ValueError("Cannot build email from empty normalized value.")
    return cleaned
