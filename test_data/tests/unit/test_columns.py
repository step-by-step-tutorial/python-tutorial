

from pathlib import Path
from random import Random

import pytest

from config_manager import ColumnConfig
from columns import build_column_generator
from data_converter import convert_to_email, convert_to_floats
from sources import SourceRepository


def build(column: ColumnConfig, root: Path):
    return build_column_generator(column, SourceRepository(root), Random(1))


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("Emily Johnson", "emily.johnson"), ("Alyssa", "alyssa"), ("  O'Neill  ", "o.neill")],
)
def test_normalize_for_email(raw: str, expected: str) -> None:
    assert convert_to_email(raw) == expected


def test_normalize_for_email_rejects_empty_result() -> None:
    with pytest.raises(ValueError, match="empty normalized value"):
        convert_to_email("###")


def test_convert_to_floats() -> None:
    assert convert_to_floats(["2", "3.5", "0"]) == [2.0, 3.5, 0.0]


def test_sequence_uses_start_and_step(tmp_path: Path) -> None:
    generator = build(ColumnConfig(name="id", type="sequence", start=10, step=5), tmp_path)

    assert [generator.generate({}, index) for index in range(3)] == ["10", "15", "20"]


def test_sequence_defaults_to_one(tmp_path: Path) -> None:
    generator = build(ColumnConfig(name="id", type="sequence"), tmp_path)

    assert generator.generate({}, 0) == "1"


def test_fixed_requires_value(tmp_path: Path) -> None:
    with pytest.raises(Exception, match="requires: value"):
        build(ColumnConfig(name="country", type="fixed"), tmp_path)


def test_random_int_requires_min_and_max(tmp_path: Path) -> None:
    with pytest.raises(Exception, match="requires: min, max"):
        build(ColumnConfig(name="quantity", type="random_int"), tmp_path)


def test_random_int_rejects_inverted_range(tmp_path: Path) -> None:
    with pytest.raises(Exception, match="'min' must not be greater than 'max'"):
        build(ColumnConfig(name="quantity", type="random_int", min=5, max=1), tmp_path)


def test_random_int_stays_within_bounds(tmp_path: Path) -> None:
    generator = build(ColumnConfig(name="quantity", type="random_int", min=1, max=5), tmp_path)

    assert all(1 <= int(generator.generate({}, index)) <= 5 for index in range(50))


def test_random_date_rejects_inverted_range(tmp_path: Path) -> None:
    with pytest.raises(Exception, match="date_start must be earlier"):
        build(
            ColumnConfig(
                name="order_date",
                type="random_date",
                date_start="2026-02-01",
                date_end="2026-01-01",
            ),
            tmp_path,
        )


def test_random_date_rejects_unparsable_date(tmp_path: Path) -> None:
    with pytest.raises(Exception, match="needs ISO dates"):
        build(
            ColumnConfig(
                name="order_date", type="random_date", date_start="01/05/2026", date_end="2026-01-31"
            ),
            tmp_path,
        )


def test_random_date_stays_within_range(tmp_path: Path) -> None:
    generator = build(
        ColumnConfig(
            name="order_date", type="random_date", date_start="2026-01-05", date_end="2026-01-07"
        ),
        tmp_path,
    )

    assert {generator.generate({}, index) for index in range(50)} <= {
        "2026-01-05",
        "2026-01-06",
        "2026-01-07",
    }


def test_random_from_file_reports_empty_source(tmp_path: Path, write_lines) -> None:
    write_lines(tmp_path / "data" / "empty.txt", "", "   ")
    generator = build(
        ColumnConfig(name="country", type="random_from_file", file="data/empty.txt"), tmp_path
    )

    with pytest.raises(Exception, match="Source file is empty"):
        generator.generate({}, 0)


def test_random_from_file_reports_missing_source(tmp_path: Path) -> None:
    generator = build(
        ColumnConfig(name="country", type="random_from_file", file="data/absent.txt"), tmp_path
    )

    with pytest.raises(Exception, match="Source file not found"):
        generator.generate({}, 0)


def test_mapped_file_rejects_both_file_keys(tmp_path: Path) -> None:
    with pytest.raises(Exception):
        build(
            ColumnConfig(
                name="name",
                type="random_from_mapped_file",
                source_field="country",
                mapping_file="data/map.csv",
                key_column="country",
                file_column="name_file",
                file_columns=("name_file",),
            ),
            tmp_path,
        )


def test_mapped_file_requires_a_file_key(tmp_path: Path) -> None:
    with pytest.raises(Exception):
        build(
            ColumnConfig(
                name="name",
                type="random_from_mapped_file",
                source_field="country",
                mapping_file="data/map.csv",
                key_column="country",
            ),
            tmp_path,
        )


def test_mapped_file_reports_unmapped_source_value(project_root: Path) -> None:
    generator = build(
        ColumnConfig(
            name="customer_name",
            type="random_from_mapped_file",
            source_field="country",
            mapping_file="data/country_source_map.csv",
            key_column="country",
            file_column="first_name_file",
        ),
        project_root,
    )

    with pytest.raises(Exception, match="'Japan' not found in mapping"):
        generator.generate({"country": "Japan"}, 0)


def test_lookup_reports_mapping_without_the_requested_column(project_root: Path) -> None:
    generator = build(
        ColumnConfig(
            name="category",
            type="derived",
            method="lookup_from_csv",
            source_field="product_name",
            mapping_file="data/product_catalog.csv",
            key_column="product",
            value_column="absent_column",
        ),
        project_root,
    )

    with pytest.raises(Exception, match="must contain columns"):
        generator.generate({"product_name": "Laptop"}, 0)


def test_product_column_uses_float_conversion_for_source_fields(project_root: Path) -> None:
    generator = build(
        ColumnConfig(
            name="subtotal",
            type="derived",
            method="product_of_source_fields",
            source_fields=("quantity", "unit_price"),
        ),
        project_root,
    )

    assert generator.generate({"quantity": "2", "unit_price": "10.5"}, 0) == "21.0"


def test_formula_column_uses_source_fields(project_root: Path) -> None:
    generator = build(
        ColumnConfig(
            name="total_amount",
            type="derived",
            method="formula",
            source_fields=("base", "rate", "fee", "extra"),
            formula="values[0] - values[0] * values[1] / 100 + values[2] + values[3]",
        ),
        project_root,
    )

    assert (
        generator.generate(
            {
                "base": "20",
                "rate": "10",
                "fee": "5",
                "extra": "2",
            },
            0,
        )
        == "25.0"
    )


def test_email_declares_its_dependencies(tmp_path: Path) -> None:
    generator = build(
        ColumnConfig(
            name="email",
            type="derived",
            method="email_from_source_fields",
            source_fields=("given", "family", "region"),
        ),
        tmp_path,
    )

    assert generator.dependencies == ("given", "family", "region")
    assert generator.generate({"given": "Lea", "family": "Bauer", "region": "EU"}, 0) == (
        "lea.bauer.eu@example.com"
    )


def test_email_uses_configured_domain(tmp_path: Path) -> None:
    generator = build(
        ColumnConfig(
            name="work_email",
            type="derived",
            method="email_from_source_fields",
            source_fields=("given", "family"),
            domain="example-corp.com",
        ),
        tmp_path,
    )

    assert generator.generate({"given": "Lea", "family": "Bauer"}, 0) == (
        "lea.bauer@example-corp.com"
    )


def test_email_reports_empty_name(tmp_path: Path) -> None:
    generator = build(
        ColumnConfig(
            name="email",
            type="derived",
            method="email_from_source_fields",
            source_fields=("given", "family"),
        ),
        tmp_path,
    )

    with pytest.raises(Exception, match="depends on source field given"):
        generator.generate({"given": "", "family": "Bauer"}, 0)


@pytest.mark.parametrize(
    ("column", "message"),
    [
        (ColumnConfig(name="x", type="magic"), "Unsupported column type: magic"),
        (ColumnConfig(name="x", type="derived", method="magic"), "Unsupported derived method"),
        (ColumnConfig(name="x", type="derived"), "needs a 'method'"),
    ],
)
def test_unknown_types_are_rejected(column: ColumnConfig, message: str, tmp_path: Path) -> None:
    with pytest.raises(Exception, match=message):
        build(column, tmp_path)
