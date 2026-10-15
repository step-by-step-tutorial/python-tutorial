

from pathlib import Path
import pytest

from testdata_platform.generator.column.column_generator_registry import ColumnGeneratorRegistry
from testdata_platform.model.column_model import ColumnModel
from testdata_platform.model.settings_model import SettingsModel
from testdata_platform.repository.source_repository import SourceRepository


def build(column: ColumnModel, source_repository: SourceRepository | None = None):
    settings = SettingsModel.from_env()
    return ColumnGeneratorRegistry(settings, source_repository or SourceRepository(settings)).get_one(column)


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


def test_random_float_stays_within_bounds() -> None:
    generator = build(ColumnModel(name="latitude", type="random_float", min=10, max=20))

    assert all(10 <= float(generator.generate({}, index)) <= 20 for index in range(50))


def test_random_bool_generates_boolean_literals() -> None:
    generator = build(ColumnModel(name="enabled", type="random_bool"))

    assert {generator.generate({}, index) for index in range(50)} <= {"True", "False"}


def test_nullable_column_can_generate_blank_values() -> None:
    generator = build(
        ColumnModel(name="floor", type="random_int", min=1, max=5, nullable=True, null_probability=1)
    )

    assert generator.generate({}, 0) == ""


def test_random_timestamp_uses_iso_timestamp_format() -> None:
    generator = build(
        ColumnModel(
            name="created_at",
            type="random_timestamp",
            date_start="2026-01-01",
            date_end="2026-01-01",
        )
    )

    assert generator.generate({}, 0).startswith("2026-01-01T")


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

    assert generator.generate({"quantity": "2", "unit_price": "10.25"}, 0) == "20.5"


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
        == "25"
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


def test_concat_from_source_fields_joins_values() -> None:
    generator = build(
        ColumnModel(
            name="address",
            type="derived",
            method="concat_from_source_fields",
            source_fields=("street", "house_number"),
        )
    )

    assert generator.generate({"street": "Sunset Boulevard", "house_number": "101"}, 0) == "Sunset Boulevard 101"


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


def test_random_from_directory_uses_non_excluded_directories(project_root: Path) -> None:
    (project_root / "data" / "regions" / "California").mkdir(parents=True)
    (project_root / "data" / "regions" / "Nevada").mkdir()
    (project_root / "data" / "regions" / "_metadata").mkdir()

    generator = build(
        ColumnModel(
            name="state",
            type="random_from_directory",
            file="data/regions",
            exclude_directories=("_metadata",),
        )
    )

    assert generator.generate({}, 0) in {"California", "Nevada"}


def test_filtered_mapped_rows_do_not_share_cache_with_other_filters(project_root: Path, write_lines) -> None:
    path = project_root / "data" / "regions" / "California" / "data.csv"
    path.parent.mkdir(parents=True)
    write_lines(
        path,
        "state,name,feature_class",
        "California,Sunset Road,R",
        "California,Los Angeles,P",
    )

    street = build(
        ColumnModel(
            name="street",
            type="random_from_mapped_csv",
            source_field="state",
            file_template="data/regions/{state}/data.csv",
            key_column="state",
            value_column="name",
            filter_column="feature_class",
            filter_values=("R",),
        )
    )
    city = build(
        ColumnModel(
            name="city",
            type="random_from_mapped_csv",
            source_field="state",
            file_template="data/regions/{state}/data.csv",
            key_column="state",
            value_column="name",
            filter_column="feature_class",
            filter_values=("P",),
        )
    )

    assert street.generate({"state": "California"}, 0) == "Sunset Road"
    assert city.generate({"state": "California"}, 0) == "Los Angeles"


def test_filtered_mapped_rows_use_configured_fallback(project_root: Path, write_lines) -> None:
    path = project_root / "data" / "regions" / "Canada" / "data.csv"
    path.parent.mkdir(parents=True)
    write_lines(path, "state,name,feature_class", "Canada,Ottawa,P")

    generator = build(
        ColumnModel(
            name="street",
            type="random_from_mapped_csv",
            source_field="state",
            file_template="data/regions/{state}/data.csv",
            key_column="state",
            value_column="name",
            filter_column="feature_class",
            filter_values=("R",),
            filter_fallback_values=("P",),
        )
    )

    assert generator.generate({"state": "Canada"}, 0) == "Ottawa"


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


def test_formula_column_rejects_code(project_root: Path) -> None:
    with pytest.raises(ValueError, match="invalid formula"):
        build(
            ColumnModel(
                name="total_amount",
                type="derived",
                method="formula",
                source_fields=("base",),
                formula="__import__('os').getcwd()",
            ),
        )


def test_columns_of_the_same_shape_get_independent_values(project_root: Path) -> None:
    first = build(ColumnModel(name="first", type="random_int", min=1, max=1_000_000))
    second = build(ColumnModel(name="second", type="random_int", min=1, max=1_000_000))

    first_values = [first.generate({}, index) for index in range(20)]
    second_values = [second.generate({}, index) for index in range(20)]

    assert first_values != second_values


def test_columns_are_reproducible_across_runs(project_root: Path) -> None:
    model = ColumnModel(name="amount", type="random_int", min=1, max=1_000_000)

    assert [build(model).generate({}, 0) for _ in range(2)] == [build(model).generate({}, 0)] * 2


def test_nullable_columns_are_null_in_different_rows(project_root: Path) -> None:
    first = build(ColumnModel(name="first", type="fixed", value="x", nullable=True, null_probability=0.5))
    second = build(ColumnModel(name="second", type="fixed", value="x", nullable=True, null_probability=0.5))

    first_nulls = [first.generate({}, index) == "" for index in range(50)]
    second_nulls = [second.generate({}, index) == "" for index in range(50)]

    assert first_nulls != second_nulls


def test_date_with_random_day_offset_uses_min_and_max_days(project_root: Path) -> None:
    generator = build(
        ColumnModel(
            name="delivery_date",
            type="derived",
            method="date_with_random_day_offset",
            source_field="order_date",
            min=3,
            max=3,
        ),
    )

    assert generator.generate({"order_date": "2026-01-01"}, 0) == "2026-01-04"


def test_date_with_random_day_offset_keeps_the_time_of_a_timestamp(project_root: Path) -> None:
    generator = build(
        ColumnModel(
            name="updated_at",
            type="derived",
            method="date_with_random_day_offset",
            source_field="created_at",
            min=1,
            max=1,
        ),
    )

    assert generator.generate({"created_at": "2026-01-01T10:20:30"}, 0) == "2026-01-02T10:20:30"


def test_random_int_reads_its_bounds_from_fields() -> None:
    generator = build(ColumnModel(name="bedroom_count", type="random_int", min=0, max_field="room_count"))

    assert generator.dependencies == ("room_count",)
    assert all(0 <= int(generator.generate({"room_count": "2"}, index)) <= 2 for index in range(50))


def test_random_float_reads_its_bounds_from_fields() -> None:
    generator = build(ColumnModel(name="living_area", type="random_float", min=10, max_field="area"))

    assert all(10 <= float(generator.generate({"area": "20.5"}, index)) <= 20.5 for index in range(50))


def test_random_int_requires_each_bound_or_its_field() -> None:
    with pytest.raises(Exception):
        build(ColumnModel(name="floor", type="random_int", min=1))


def test_present_when_leaves_the_column_blank_unless_the_flag_is_true() -> None:
    generator = build(
        ColumnModel(name="garage_capacity", type="random_int", min=1, max=1, present_when="has_garage")
    )

    assert "has_garage" in generator.dependencies
    assert generator.generate({"has_garage": "True"}, 0) == "1"
    assert generator.generate({"has_garage": "False"}, 0) == ""


def test_mapped_csv_columns_of_one_record_share_the_selected_row(project_root: Path, write_lines) -> None:
    write_lines(
        project_root / "data" / "addresses.csv",
        "state,street,city",
        *(f"CA,Street {index},City {index}" for index in range(20)),
    )
    settings = SettingsModel.from_env()
    source_repository = SourceRepository(settings)
    common = {"type": "random_from_mapped_csv", "source_field": "state", "mapping_file": "data/addresses.csv",
              "key_column": "state"}
    street = build(ColumnModel(name="street", value_column="street", **common), source_repository)
    city = build(ColumnModel(name="city", value_column="city", **common), source_repository)

    for row_index in range(10):
        street_value = street.generate({"state": "CA"}, row_index)
        city_value = city.generate({"state": "CA"}, row_index)
        assert street_value.split()[-1] == city_value.split()[-1]
