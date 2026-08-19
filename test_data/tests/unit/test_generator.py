

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


def test_generate_dataset_writes_json_when_requested(tmp_path: Path) -> None:
    (tmp_path / "config_sample.json").write_text(
        """
        {
          "row_count": 2,
          "output_file": "output/sample.csv",
          "destinations": ["csv", "json"],
          "columns": [
            {"name": "id", "type": "sequence", "start": 1, "step": 1},
            {"name": "country", "type": "fixed", "value": "USA"}
          ]
        }
        """.strip(),
        encoding="utf-8",
    )

    result = generate_dataset(tmp_path / "config_sample.json")

    assert result.row_count == 2
    assert result.output_path.read_text(encoding="utf-8").splitlines() == [
        "id,country",
        "1,USA",
        "2,USA",
    ]
    assert (tmp_path / "output" / "sample.json").is_file()
    assert result.output_path.parent == tmp_path / "output"


def test_generate_dataset_supports_online_shopping_pricing_fields(tmp_path: Path, mocker) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    (data_dir / "payment_statuses.txt").write_text("Paid\n", encoding="utf-8")
    (data_dir / "fulfillment_statuses.txt").write_text("Shipped\n", encoding="utf-8")

    (tmp_path / "config_online.json").write_text(
        """
        {
          "row_count": 1,
          "output_file": "output/online.csv",
          "destinations": ["csv", "json", "database"],
          "seed": 1,
          "columns": [
            {"name": "order_id", "type": "sequence", "start": 1, "step": 1},
            {"name": "order_date", "type": "fixed", "value": "2026-01-10"},
            {"name": "product_name", "type": "fixed", "value": "Laptop"},
            {"name": "quantity", "type": "fixed", "value": "2"},
            {"name": "unit_price", "type": "fixed", "value": "10"},
            {"name": "subtotal", "type": "derived", "method": "subtotal_from_quantity_and_unit_price"},
            {"name": "discount_percent", "type": "fixed", "value": "10"},
            {"name": "shipping_cost", "type": "fixed", "value": "5"},
            {"name": "tax_amount", "type": "derived", "method": "tax_from_subtotal", "value": 0.1},
            {"name": "total_amount", "type": "derived", "method": "total_amount"},
            {"name": "payment_status", "type": "random_from_file", "file": "data/payment_statuses.txt"},
            {"name": "fulfillment_status", "type": "random_from_file", "file": "data/fulfillment_statuses.txt"},
            {
              "name": "estimated_delivery_date",
              "type": "derived",
              "method": "delivery_date_from_order_date",
              "source_field": "order_date",
              "start": 2,
              "step": 2
            }
          ]
        }
        """.strip(),
        encoding="utf-8",
    )

    database_repository = mocker.patch("generator.DatabaseRepository")
    generate_dataset(tmp_path / "config_online.json")

    output_path = tmp_path / "output" / "online.csv"
    assert output_path.read_text(encoding="utf-8").splitlines() == [
        "order_id,order_date,product_name,quantity,unit_price,subtotal,discount_percent,shipping_cost,tax_amount,total_amount,payment_status,fulfillment_status,estimated_delivery_date",
        "1,2026-01-10,Laptop,2,10,20.0,10,5,2.0,25.0,Paid,Shipped,2026-01-12",
    ]
    assert (tmp_path / "output" / "online.json").is_file()
    assert database_repository.return_value.write_rows.call_count == 1
