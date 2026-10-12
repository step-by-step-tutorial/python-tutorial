from datetime import date, timedelta
from random import Random


def days_between(start: date, end: date, error_message: str = "start must be earlier than or equal to end") -> int:
    """Return the days from start to end; raise ValueError when end is before start."""
    if start > end:
        raise ValueError(error_message)
    return (end - start).days


def random_date_between(start: date, end: date, random: Random) -> str:
    offset = random.randint(0, days_between(start, end))
    return (start + timedelta(days=offset)).isoformat()


def random_date_from(base_date: date, min_days: int, max_days: int, random: Random) -> str:
    offset = random.randint(min_days, max_days)
    return (base_date + timedelta(days=offset)).isoformat()
