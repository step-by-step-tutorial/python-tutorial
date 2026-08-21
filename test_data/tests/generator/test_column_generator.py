

from pathlib import Path
import pytest

from test_data.generator.column_generator_registry import ColumnGeneratorRegistry
from test_data.model.schemas import ColumnModel


def build(column: ColumnModel):
    return ColumnGeneratorRegistry.get_one(column)


def test_sequence_uses_start_and_step() -> None:
    generator = build(ColumnModel(name="id", type="sequence", start=10, step=5))

    assert [generator.generate({}, index) for index in range(3)] == ["10", "15", "20"]


def test_sequence_defaults_to_one() -> None:
    generator = build(ColumnModel(name="id", type="sequence"))

    assert generator.generate({}, 0) == "1"


def test_fixed_requires_value() -> None:
    with pytest.raises(Exception):
        build(ColumnModel(name="country", type="fixed"))


def test_random_int_requires_min_and_max() -> None:
    with pytest.raises(Exception):
        build(ColumnModel(name="quantity", type="random_int"))


def test_random_int_rejects_inverted_range() -> None:
    with pytest.raises(Exception):
        build(ColumnModel(name="quantity", type="random_int", min=5, max=1))


def test_random_int_stays_within_bounds() -> None:
    generator = build(ColumnModel(name="quantity", type="random_int", min=1, max=5))

    assert all(1 <= int(generator.generate({}, index)) <= 5 for index in range(50))


def test_random_date_rejects_inverted_range() -> None:
    with pytest.raises(Exception):
        build(
            ColumnModel(
                name="order_date",
                type="random_date",
                date_start="2026-02-01",
                date_end="2026-01-01",
            ),
        )


def test_random_date_rejects_unparsable_date() -> None:
    with pytest.raises(Exception):
        build(
            ColumnModel(
                name="order_date", type="random_date", date_start="01/05/2026", date_end="2026-01-31"
            ),
        )


def test_random_date_stays_within_range() -> None:
    generator = build(
        ColumnModel(
            name="order_date", type="random_date", date_start="2026-01-05", date_end="2026-01-07"
        ),
    )

    assert {generator.generate({}, index) for index in range(50)} <= {
        "2026-01-05",
        "2026-01-06",
        "2026-01-07",
    }


def test_random_from_file_reports_empty_source(project_root: Path, write_lines) -> None:
    write_lines(project_root / "data" / "empty.txt", "", "   ")
    generator = build(
        ColumnModel(name="country", type="random_from_file", file="data/empty.txt")
    )

    with pytest.raises(Exception):
        generator.generate({}, 0)


def test_random_from_file_reports_missing_source(project_root: Path) -> None:
    generator = build(
        ColumnModel(name="country", type="random_from_file", file="data/absent.txt")
    )

    with pytest.raises(Exception):
        generator.generate({}, 0)


def test_mapped_file_rejects_both_file_keys() -> None:
    with pytest.raises(Exception):
        build(
            ColumnModel(
                name="name",
                type="random_from_mapped_file",
                source_field="country",
                mapping_file="data/map.csv",
                key_column="country",
                file_column="name_file",
                file_columns=("name_file",),
            ),
        )


def test_mapped_file_requires_a_file_key() -> None:
    with pytest.raises(Exception):
        build(
            ColumnModel(
                name="name",
                type="random_from_mapped_file",
                source_field="country",
                mapping_file="data/map.csv",
                key_column="country",
            ),
        )


def test_mapped_file_reports_unmapped_source_value(project_root: Path) -> None:
    generator = build(
        ColumnModel(
            name="customer_name",
            type="random_from_mapped_file",
            source_field="country",
            mapping_file="data/country_source_map.csv",
            key_column="country",
            file_column="first_name_file",
        ),
    )

    with pytest.raises(Exception):
        generator.generate({"country": "Japan"}, 0)


def test_lookup_reports_mapping_without_the_requested_column(project_root: Path) -> None:
    generator = build(
        ColumnModel(
            name="category",
            type="derived",
            method="lookup_from_csv",
            source_field="product_name",
            mapping_file="data/product_catalog.csv",
            key_column="product",
            value_column="absent_column",
        ),
    )

    with pytest.raises(Exception):
        generator.generate({"product_name": "Laptop"}, 0)


def test_product_column_uses_float_conversion_for_source_fields(project_root: Path) -> None:
    generator = build(
        ColumnModel(
            name="subtotal",
            type="derived",
            method="product_of_source_fields",
            source_fields=("quantity", "unit_price"),
        ),
    )

    assert generator.generate({"quantity": "2", "unit_price": "10.5"}, 0) == "21.0"


def test_formula_column_uses_source_fields(project_root: Path) -> None:
    generator = build(
        ColumnModel(
            name="total_amount",
            type="derived",
            method="formula",
            source_fields=("base", "rate", "fee", "extra"),
            formula="values[0] - values[0] * values[1] / 100 + values[2] + values[3]",
        ),
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


def test_email_declares_its_dependencies() -> None:
    generator = build(
        ColumnModel(
            name="email",
            type="derived",
            method="email_from_source_fields",
            source_fields=("given", "family", "region"),
        ),
    )

    assert generator.dependencies == ("given", "family", "region")
    assert generator.generate({"given": "Lea", "family": "Bauer", "region": "EU"}, 0) == (
        "lea.bauer.eu@example.com"
    )


def test_email_uses_configured_domain() -> None:
    generator = build(
        ColumnModel(
            name="work_email",
            type="derived",
            method="email_from_source_fields",
            source_fields=("given", "family"),
            domain="example-corp.com",
        ),
    )

    assert generator.generate({"given": "Lea", "family": "Bauer"}, 0) == (
        "lea.bauer@example-corp.com"
    )


def test_email_reports_empty_name() -> None:
    generator = build(
        ColumnModel(
            name="email",
            type="derived",
            method="email_from_source_fields",
            source_fields=("given", "family"),
        ),
    )

    with pytest.raises(Exception):
        generator.generate({"given": "", "family": "Bauer"}, 0)


@pytest.mark.parametrize(
    "column",
    [
        ColumnModel(name="x", type="magic"),
        ColumnModel(name="x", type="derived", method="magic"),
        ColumnModel(name="x", type="derived"),
    ],
)
def test_unknown_types_are_rejected(column: ColumnModel) -> None:
    with pytest.raises(Exception):
        build(column)
