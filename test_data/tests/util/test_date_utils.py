from datetime import date
from random import Random

import pytest

from test_data.util.date_utils import days_between, random_date_between, random_date_from


def test_days_between() -> None:
    assert days_between(date(2024, 1, 1), date(2024, 1, 31)) == 30

    with pytest.raises(ValueError):
        days_between(date(2024, 2, 1), date(2024, 1, 1))


def test_random_dates_stay_in_range() -> None:
    random = Random(1)

    assert "2024-01-01" <= random_date_between(date(2024, 1, 1), date(2024, 1, 3), random) <= "2024-01-03"
    assert "2024-01-02" <= random_date_from(date(2024, 1, 1), 1, 2, random) <= "2024-01-03"
