import pytest

from test_data.util.text_utils import to_email_local_part


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("Emily Johnson", "emily.johnson"), ("Alyssa", "alyssa"), ("  O'Neill  ", "o.neill")],
)
def test_to_email_local_part(raw: str, expected: str) -> None:
    assert to_email_local_part(raw) == expected


def test_to_email_local_part_rejects_empty_result() -> None:
    with pytest.raises(ValueError):
        to_email_local_part("###")

