"""Tests for row generation, dependency resolution, and CSV export."""


import csv
from pathlib import Path

import pytest

from application_config import ColumnConfig, load_config, GeneratorConfig
from exceptions import DependencyError
from generator import CsvDataGenerator, generate_dataset


def make_generator(columns: list[ColumnConfig], root: Path, row_count: int = 1) -> CsvDataGenerator:
    config = GeneratorConfig(
        row_count=row_count,
        output_file="output/test.csv",
        columns=columns,
        seed=1,
    )
    return CsvDataGenerator(config=config, project_root=root)


def test_generate_rows_follows_config_column_order(project_root: Path) -> None:
    config = load_config(project_root / "config_demo.json")
    rows = CsvDataGenerator(config=config, project_root=project_root).generate_rows()

    assert len(rows) == 5
    assert list(rows[0]) == list(config.headers)


def test_country_dependent_columns_stay_consistent(project_root: Path) -> None:
    config = load_config(project_root / "config_demo.json")
    rows = CsvDataGenerator(config=config, project_root=project_root).generate_rows()

    expected = {"Germany": {"Hans Bauer"}, "USA": {"John Smith"}}
    for row in rows:
        assert row["customer_name"] in expected[row["country"]]


def test_column_may_be_declared_before_its_dependency(project_root: Path) -> None:
    generator = make_generator(
        [
            ColumnConfig(
                name="customer_name",
                type="random_from_mapped_file",
                source_field="country",
                mapping_file="data/country_source_map.csv",
                key_column="country",
                file_column="first_name_file",
            ),
            ColumnConfig(name="country", type="fixed", value="Germany"),
        ],
        project_root,
    )

    assert generator.generate_rows() == [{"customer_name": "Hans", "country": "Germany"}]


def test_mapped_file_joins_several_file_columns(project_root: Path) -> None:
    generator = make_generator(
        [
            ColumnConfig(name="country", type="fixed", value="Germany"),
            ColumnConfig(
                name="customer_name",
                type="random_from_mapped_file",
                source_field="country",
                mapping_file="data/country_source_map.csv",
                key_column="country",
                file_columns=("first_name_file", "last_name_file"),
                separator=", ",
            ),
        ],
        project_root,
    )

    assert generator.generate_rows()[0]["customer_name"] == "Hans, Bauer"


def test_derived_email_uses_generated_names(project_root: Path) -> None:
    generator = make_generator(
        [
            ColumnConfig(
                name="first_name",
                type="random_from_mapped_file",
                source_field="country",
                mapping_file="data/country_source_map.csv",
                key_column="country",
                file_column="first_name_file",
            ),
            ColumnConfig(
                name="last_name",
                type="random_from_mapped_file",
                source_field="country",
                mapping_file="data/country_source_map.csv",
                key_column="country",
                file_column="last_name_file",
            ),
            ColumnConfig(
                name="email", type="derived", method="email_from_name", domain="example-shop.com"
            ),
            ColumnConfig(name="country", type="fixed", value="USA"),
        ],
        project_root,
    )

    assert generator.generate_rows()[0]["email"] == "john.smith@example-shop.com"


def test_circular_dependencies_are_rejected_before_generating(tmp_path: Path) -> None:
    with pytest.raises(DependencyError, match="Circular column dependency detected"):
        make_generator(
            [
                ColumnConfig(
                    name="left",
                    type="derived",
                    method="lookup_from_csv",
                    source_field="right",
                    mapping_file="data/map.csv",
                    key_column="key",
                    value_column="value",
                ),
                ColumnConfig(
                    name="right",
                    type="derived",
                    method="lookup_from_csv",
                    source_field="left",
                    mapping_file="data/map.csv",
                    key_column="key",
                    value_column="value",
                ),
            ],
            tmp_path,
        )


def test_unknown_dependency_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(DependencyError, match="depends on unknown column 'country'"):
        make_generator(
            [
                ColumnConfig(
                    name="currency",
                    type="derived",
                    method="lookup_from_csv",
                    source_field="country",
                    mapping_file="data/map.csv",
                    key_column="country",
                    value_column="currency_code",
                )
            ],
            tmp_path,
        )


def test_write_csv_writes_header_and_rows(tmp_path: Path) -> None:
    generator = make_generator([ColumnConfig(name="country", type="fixed", value="Germany")], tmp_path)
    output_path = generator.write_csv([{"country": "Germany"}])

    assert output_path == tmp_path / "output" / "test.csv"
    assert output_path.read_text(encoding="utf-8").splitlines() == ["country", "Germany"]


def test_generate_streams_rows_and_reports_the_count(project_root: Path) -> None:
    config = load_config(project_root / "config_demo.json")
    result = CsvDataGenerator(config=config, project_root=project_root).generate()

    assert result.row_count == 5
    assert result.output_path == project_root / "output" / "demo.csv"
    with result.output_path.open(encoding="utf-8", newline="") as file:
        assert len(list(csv.DictReader(file))) == 5


def test_seeded_runs_are_reproducible(project_root: Path) -> None:
    config = load_config(project_root / "config_demo.json")
    first = CsvDataGenerator(config=config, project_root=project_root).generate_rows()
    second = CsvDataGenerator(config=config, project_root=project_root).generate_rows()

    assert first == second


def test_zero_rows_writes_header_only(project_root: Path) -> None:
    generator = make_generator(
        [ColumnConfig(name="country", type="fixed", value="Germany")], project_root, row_count=0
    )
    result = generator.generate()

    assert result.row_count == 0
    assert result.output_path.read_text(encoding="utf-8").splitlines() == ["country"]


def test_generate_dataset_loads_the_config_and_writes_the_file(project_root: Path) -> None:
    result = generate_dataset(project_root / "config_demo.json")

    assert result.row_count == 5
    assert result.output_path.is_file()
