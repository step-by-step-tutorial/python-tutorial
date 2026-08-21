import json
import importlib
from dataclasses import asdict
from pathlib import Path

import pytest
import env_config

from dataset_generator import DatasetGenerator
from schemas import ColumnModel, ConfigModel


def write_config_file(tmp_path: Path, name: str, config: ConfigModel) -> str:
    def clean(value):
        if isinstance(value, dict):
            return {key: clean(val) for key, val in value.items() if val is not None}
        if isinstance(value, list):
            return [clean(item) for item in value]
        if isinstance(value, tuple):
            return [clean(item) for item in value]
        return value

    config_name = f"test_output/{name}"
    config_path = tmp_path / "config" / config_name
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(json.dumps(clean(asdict(config))), encoding="utf-8")
    return config_name


def config_with_headers(**kwargs) -> ConfigModel:
    return ConfigModel(
        name=kwargs.pop("name", "generated.json"),
        column_names=tuple(column.name for column in kwargs["columns"]),
        kafka_topic=kwargs.pop("kafka_topic", "test-events"),
        kafka_key_column=kwargs.pop("kafka_key_column", "id"),
        **kwargs,
    )


def make_generator(columns: list[ColumnModel], row_count: int = 1) -> DatasetGenerator:
    config = config_with_headers(
        row_count=row_count,
        output_name="generated",
        columns=columns,
        destinations=("csv",),
    )
    return DatasetGenerator(write_config_file(Path(env_config.CONFIG_DIR).parent, "generated.json", config))


def test_generate_rows_follows_config_column_order(project_root: Path) -> None:
    rows = list(DatasetGenerator("demo.json").row_generator.generate_rows())

    assert len(rows) == 5
    assert list(rows[0]) == ["order_id", "customer_name", "product_name", "category", "country"]


def test_country_dependent_columns_stay_consistent(project_root: Path) -> None:
    rows = list(DatasetGenerator("demo.json").row_generator.generate_rows())

    expected = {"Germany": {"Hans Bauer"}, "USA": {"John Smith"}}
    for row in rows:
        assert row["customer_name"] in expected[row["country"]]


def test_column_may_be_declared_before_its_dependency(project_root: Path) -> None:
    generator = make_generator(
        [
            ColumnModel(
                name="customer_name",
                type="random_from_mapped_file",
                source_field="country",
                mapping_file="data/country_source_map.csv",
                key_column="country",
                file_column="first_name_file",
            ),
            ColumnModel(name="country", type="fixed", value="Germany"),
        ],
    )

    assert list(generator.row_generator.generate_rows()) == [{"customer_name": "Hans", "country": "Germany"}]


def test_mapped_file_joins_several_file_columns(project_root: Path) -> None:
    generator = make_generator(
        [
            ColumnModel(name="country", type="fixed", value="Germany"),
            ColumnModel(
                name="customer_name",
                type="random_from_mapped_file",
                source_field="country",
                mapping_file="data/country_source_map.csv",
                key_column="country",
                file_columns=("first_name_file", "last_name_file"),
                separator=", ",
            ),
        ],
    )

    assert list(generator.row_generator.generate_rows())[0]["customer_name"] == "Hans, Bauer"


def test_derived_email_uses_generated_names(project_root: Path) -> None:
    generator = make_generator(
        [
            ColumnModel(
                name="first_name",
                type="random_from_mapped_file",
                source_field="country",
                mapping_file="data/country_source_map.csv",
                key_column="country",
                file_column="first_name_file",
            ),
            ColumnModel(
                name="last_name",
                type="random_from_mapped_file",
                source_field="country",
                mapping_file="data/country_source_map.csv",
                key_column="country",
                file_column="last_name_file",
            ),
            ColumnModel(
                name="email",
                type="derived",
                method="email_from_source_fields",
                source_fields=("first_name", "last_name"),
                domain="example-shop.com",
            ),
            ColumnModel(name="country", type="fixed", value="USA"),
        ],
    )

    assert list(generator.row_generator.generate_rows())[0]["email"] == "john.smith@example-shop.com"


def test_circular_dependencies_are_rejected_before_generating(tmp_path: Path) -> None:
    with pytest.raises(Exception):
        make_generator(
            [
                ColumnModel(
                    name="left",
                    type="derived",
                    method="lookup_from_csv",
                    source_field="right",
                    mapping_file="data/map.csv",
                    key_column="key",
                    value_column="value",
                ),
                ColumnModel(
                    name="right",
                    type="derived",
                    method="lookup_from_csv",
                    source_field="left",
                    mapping_file="data/map.csv",
                    key_column="key",
                    value_column="value",
                ),
            ],
        )


def test_seeded_runs_are_reproducible(project_root: Path) -> None:
    first = list(DatasetGenerator("demo.json").row_generator.generate_rows())
    second = list(DatasetGenerator("demo.json").row_generator.generate_rows())

    assert first == second


def test_zero_rows_writes_header_only(project_root: Path) -> None:
    generator = make_generator(
        [ColumnModel(name="country", type="fixed", value="Germany")], row_count=0
    )

    assert list(generator.row_generator.generate_rows()) == []


def test_generate_dataset_loads_the_config_and_writes_the_file(project_root: Path) -> None:
    DatasetGenerator("demo.json").write()

    assert (env_config.OUTPUT_DIR / "demo.csv").is_file()


def test_generate_dataset_writes_json_when_requested(tmp_path: Path, monkeypatch) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "sample.json").write_text(
        """
        {
          "row_count": 2,
          "output_name": "sample",
          "kafka_topic": "test-events",
          "kafka_key_column": "id",
          "destinations": ["csv", "json"],
          "columns": [
            {"name": "id", "type": "sequence", "start": 1, "step": 1},
            {"name": "country", "type": "fixed", "value": "USA"}
          ]
        }
        """.strip(),
        encoding="utf-8",
    )

    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))
    monkeypatch.setenv("CONFIG_DIR", str(config_dir))
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "output"))
    importlib.reload(env_config)

    DatasetGenerator("sample.json").write()

    output_path = tmp_path / "output" / "sample.csv"
    assert output_path.read_text(encoding="utf-8").splitlines() == [
        "id,country",
        "1,USA",
        "2,USA",
    ]
    assert (tmp_path / "output" / "sample.json").is_file()
    assert output_path.parent == tmp_path / "output"

    monkeypatch.delenv("PROJECT_ROOT", raising=False)
    monkeypatch.delenv("CONFIG_DIR", raising=False)
    monkeypatch.delenv("OUTPUT_DIR", raising=False)
    importlib.reload(env_config)


def test_generate_dataset_publishes_json_rows_to_kafka(tmp_path: Path, mocker, monkeypatch) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "sample.json").write_text(
        """
        {
          "row_count": 2,
          "output_name": "sample",
          "kafka_topic": "test-data-sample",
          "kafka_key_column": "id",
          "destinations": ["kafka"],
          "columns": [
            {"name": "id", "type": "sequence", "start": 1, "step": 1},
            {"name": "country", "type": "fixed", "value": "USA"}
          ]
        }
        """.strip(),
        encoding="utf-8",
    )

    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))
    monkeypatch.setenv("CONFIG_DIR", str(config_dir))
    importlib.reload(env_config)
    producer = mocker.patch("writer_registry.create_producer").return_value
    producer.flush.return_value = 0

    DatasetGenerator("sample.json").write()

    assert producer.produce.call_count == 2
    assert producer.produce.call_args_list[0].kwargs["topic"] == "test-data-sample"
    assert producer.produce.call_args_list[0].kwargs["key"] == "1"
    assert producer.produce.call_args_list[0].kwargs["value"] == b'{"id": "1", "country": "USA"}'
    producer.flush.assert_called_once_with()

    monkeypatch.delenv("PROJECT_ROOT", raising=False)
    monkeypatch.delenv("CONFIG_DIR", raising=False)
    importlib.reload(env_config)


def test_generate_dataset_supports_online_shopping_pricing_fields(tmp_path: Path, mocker, monkeypatch) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()

    (data_dir / "payment_statuses.txt").write_text("Paid\n", encoding="utf-8")
    (data_dir / "fulfillment_statuses.txt").write_text("Shipped\n", encoding="utf-8")

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "online.json").write_text(
        """
        {
          "row_count": 1,
          "output_name": "online",
          "kafka_topic": "test-events",
          "kafka_key_column": "order_id",
          "destinations": ["csv", "json", "database"],
          "columns": [
            {"name": "order_id", "type": "sequence", "start": 1, "step": 1},
            {"name": "order_date", "type": "fixed", "value": "2026-01-10"},
            {"name": "product_name", "type": "fixed", "value": "Laptop"},
            {"name": "quantity", "type": "fixed", "value": "2"},
            {"name": "unit_price", "type": "fixed", "value": "10"},
            {
                "name": "subtotal",
                "type": "derived",
                "method": "product_of_source_fields",
                "source_fields": ["quantity", "unit_price"]
            },
            {"name": "discount_percent", "type": "fixed", "value": "10"},
            {"name": "shipping_cost", "type": "fixed", "value": "5"},
            {
                "name": "tax_amount",
                "type": "derived",
                "method": "product_of_source_fields",
                "source_fields": ["subtotal"],
                "value": 0.1
            },
            {
                "name": "total_amount",
                "type": "derived",
                "method": "formula",
                "source_fields": ["subtotal", "discount_percent", "shipping_cost", "tax_amount"],
                "formula": "values[0] - values[0] * values[1] / 100 + values[2] + values[3]"
            },
            {"name": "payment_status", "type": "random_from_file", "file": "data/payment_statuses.txt"},
            {"name": "fulfillment_status", "type": "random_from_file", "file": "data/fulfillment_statuses.txt"},
            {
              "name": "estimated_delivery_date",
              "type": "derived",
              "method": "date_with_random_day_offset",
              "source_field": "order_date",
              "start": 2,
              "step": 2
            }
          ]
        }
        """.strip(),
        encoding="utf-8",
    )

    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))
    monkeypatch.setenv("CONFIG_DIR", str(config_dir))
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "output"))
    importlib.reload(env_config)

    database_repository = mocker.patch("writer_registry.DatabaseRepository")
    DatasetGenerator("online.json").write()

    output_path = tmp_path / "output" / "online.csv"
    assert output_path.read_text(encoding="utf-8").splitlines() == [
        "order_id,order_date,product_name,quantity,unit_price,subtotal,discount_percent,shipping_cost,tax_amount,total_amount,payment_status,fulfillment_status,estimated_delivery_date",
        "1,2026-01-10,Laptop,2,10,20.0,10,5,2.0,25.0,Paid,Shipped,2026-01-12",
    ]
    assert (tmp_path / "output" / "online.json").is_file()
    assert database_repository.return_value.write_rows.call_count == 1

    monkeypatch.delenv("PROJECT_ROOT", raising=False)
    monkeypatch.delenv("CONFIG_DIR", raising=False)
    monkeypatch.delenv("OUTPUT_DIR", raising=False)
    importlib.reload(env_config)
