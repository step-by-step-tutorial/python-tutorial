import pytest

from test_data.converter.data_converter import convert_to_email, convert_to_floats


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("Emily Johnson", "emily.johnson"), ("Alyssa", "alyssa"), ("  O'Neill  ", "o.neill")],
)
def test_convert_to_email(raw: str, expected: str) -> None:
    assert convert_to_email(raw) == expected


def test_convert_to_email_rejects_empty_result() -> None:
    with pytest.raises(ValueError):
        convert_to_email("###")


def test_convert_to_floats() -> None:
    assert convert_to_floats(["2", "3.5", "0"]) == [2.0, 3.5, 0.0]
