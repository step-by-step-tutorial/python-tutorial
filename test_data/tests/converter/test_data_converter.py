import pytest

from test_data.converter.data_converter import convert_to_email


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("Emily Johnson", "emily.johnson"), ("Alyssa", "alyssa"), ("  O'Neill  ", "o.neill")],
)
def test_convert_to_email(raw: str, expected: str) -> None:
    assert convert_to_email(raw) == expected


def test_convert_to_email_rejects_empty_result() -> None:
    with pytest.raises(ValueError):
        convert_to_email("###")

