import json
import importlib
from dataclasses import asdict
from pathlib import Path

import pytest
import env_config

from config_manager import ColumnConfig, GeneratorConfig
from generator import DataGenerator


def write_config_file(tmp_path: Path, name: str, config: GeneratorConfig) -> str:
    def clean(value):
        if isinstance(value, dict):
            return {key: clean(val) for key, val in value.items() if val is not None}
        if isinstance(value, list):
            return [clean(item) for item in value]
        if isinstance(value, tuple):
            return [clean(item) for item in value]
        return value

    config_dir = tmp_path / "config"
    config_dir.mkdir(exist_ok=True)
    (config_dir / name).write_text(json.dumps(clean(asdict(config))), encoding="utf-8")
    return name


def make_generator(columns: list[ColumnConfig], row_count: int = 1) -> DataGenerator:
    config = GeneratorConfig(
        row_count=row_count,
        output_file="generated.csv",
        columns=columns,
        destinations=("csv",),
        seed=1,
    )
    return DataGenerator(write_config_file(Path(env_config.CONFIG_DIR).parent, "generated.json", config))


def test_generate_rows_follows_config_column_order(project_root: Path) -> None:
    rows = list(DataGenerator("demo.json").iter_rows())

    assert len(rows) == 5
    assert list(rows[0]) == ["order_id", "customer_name", "product_name", "category", "country"]


def test_country_dependent_columns_stay_consistent(project_root: Path) -> None:
    rows = list(DataGenerator("demo.json").iter_rows())

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
    )

    assert list(generator.iter_rows()) == [{"customer_name": "Hans", "country": "Germany"}]


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
    )

    assert list(generator.iter_rows())[0]["customer_name"] == "Hans, Bauer"


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
                name="email",
                type="derived",
                method="email_from_source_fields",
                source_fields=("first_name", "last_name"),
                domain="example-shop.com",
            ),
            ColumnConfig(name="country", type="fixed", value="USA"),
        ],
    )

    assert list(generator.iter_rows())[0]["email"] == "john.smith@example-shop.com"


def test_circular_dependencies_are_rejected_before_generating(tmp_path: Path) -> None:
    with pytest.raises(Exception, match="Circular column dependency detected"):
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
        )


def test_unknown_dependency_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(Exception, match="depends on unknown column 'country'"):
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
        )


def test_seeded_runs_are_reproducible(project_root: Path) -> None:
    first = list(DataGenerator("demo.json").iter_rows())
    second = list(DataGenerator("demo.json").iter_rows())

    assert first == second


def test_zero_rows_writes_header_only(project_root: Path) -> None:
    generator = make_generator(
        [ColumnConfig(name="country", type="fixed", value="Germany")], row_count=0
    )

    assert list(generator.iter_rows()) == []


def test_generate_dataset_loads_the_config_and_writes_the_file(project_root: Path) -> None:
    DataGenerator("demo.json").generate_dataset()

    assert (project_root / "output" / "demo.csv").is_file()


def test_generate_dataset_writes_json_when_requested(tmp_path: Path, monkeypatch) -> None:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "sample.json").write_text(
        """
        {
          "row_count": 2,
          "output_file": "sample.csv",
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

    DataGenerator("sample.json").generate_dataset()

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
          "output_file": "online.csv",
          "destinations": ["csv", "json", "database"],
          "seed": 1,
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
    DataGenerator("online.json").generate_dataset()

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
