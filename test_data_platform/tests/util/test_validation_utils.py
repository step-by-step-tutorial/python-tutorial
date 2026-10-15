from datetime import date

import pytest

from test_data_platform.util.validation_utils import (
    default_if_blank,
    is_blank,
    require_blank,
    require_exactly_one,
    require_iso_date,
    require_key,
    require_not_blank,
    require_not_greater,
    require_not_negative,
)


@pytest.mark.parametrize("value", [None, "", [], (), {}, set()])
def test_is_blank(value) -> None:
    assert is_blank(value)


@pytest.mark.parametrize("value", [0, False, " ", ["x"], {"a": 1}])
def test_is_not_blank(value) -> None:
    assert not is_blank(value)


def test_default_if_blank() -> None:
    assert default_if_blank(None, 1) == 1
    assert default_if_blank(0, 1) == 0


def test_require_blank_and_not_blank() -> None:
    assert require_blank([]) == []
    assert require_not_blank("x") == "x"
    with pytest.raises(ValueError, match="missing"):
        require_not_blank("", "missing")
    with pytest.raises(ValueError):
        require_blank(["x"])


def test_require_key() -> None:
    assert require_key({"a": 1}, "a") == 1
    with pytest.raises(KeyError):
        require_key({}, "a")


def test_require_exactly_one() -> None:
    require_exactly_one("a", None)
    require_exactly_one(None, "b")
    with pytest.raises(ValueError):
        require_exactly_one(None, None)
    with pytest.raises(ValueError):
        require_exactly_one("a", "b")


def test_require_not_greater_and_not_negative() -> None:
    require_not_greater(1, 1)
    require_not_negative(0, 3)
    with pytest.raises(ValueError):
        require_not_greater(2, 1)
    with pytest.raises(ValueError):
        require_not_negative(1, -1)


def test_require_iso_date() -> None:
    assert require_iso_date("2024-01-31") == date(2024, 1, 31)
    with pytest.raises(ValueError):
        require_iso_date("31.01.2024")
