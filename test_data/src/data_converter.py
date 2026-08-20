import re
from datetime import date, timedelta
from random import Random

import unicodedata

NUMBER_LETTER_PATTERN = re.compile(r"[^a-z0-9]+")
REPEATED_DOTS_PATTERN = re.compile(r"\.+")


def convert_to_email(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")

    cleaned = NUMBER_LETTER_PATTERN.sub(".", ascii_value.lower().strip())
    cleaned = REPEATED_DOTS_PATTERN.sub(".", cleaned).strip(".")
    if not cleaned:
        raise ValueError("Cannot build email from empty normalized value.")
    return cleaned


def calculate_days(start: date, end: date, error_message: str = "start must be earlier than or equal to end") -> int:
    if start > end:
        raise ValueError(error_message)
    return (end - start).days


def random_date_between(start: date, end: date, random: Random) -> str:
    days = calculate_days(start, end)
    offset = random.randint(0, days)
    return (start + timedelta(days=offset)).isoformat()


def random_date_from(base_date: date, min_days:int, max_days:int, random: Random) -> str:
    offset = random.randint(min_days, max_days)
    return (base_date + timedelta(days=offset)).isoformat()


def convert_to_floats(values: list[str]) -> list[float]:
    return [float(value) for value in values]
