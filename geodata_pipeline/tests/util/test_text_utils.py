from geodata_pipeline.util.text_utils import normalize


def test_normalize_lowercases_and_collapses_whitespace() -> None:
    assert normalize("  Los   Angeles ") == "los angeles"


def test_normalize_returns_empty_text_for_missing_value() -> None:
    assert normalize(None) == ""
    assert normalize("") == ""
