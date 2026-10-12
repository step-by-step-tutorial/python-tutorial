

import json
import importlib
from pathlib import Path

import pytest
from test_data.config import settings as env_config
from test_data.model.schemas import ColumnModel, ConfigModel, Dataset, DatasetMetadata


def test_load_config_reads_columns(project_root: Path) -> None:
    config = ConfigModel.from_file("demo.json")

    assert config.name == "demo.json"
    assert config.row_count == 5
    assert config.output_name == "demo"
    assert config.column_names == ("order_id", "customer_name", "product_name", "category", "country")
    assert config.destinations == ("csv",)


def test_column_config_converts_file_columns_to_tuple() -> None:
    column = ColumnModel.from_dict(
        {
            "name": "customer_name",
            "type": "random_from_mapped_file",
            "file_columns": ["first_name_file", "last_name_file"],
        }
    )

    assert column.file_columns == ("first_name_file", "last_name_file")


def test_column_model_list_converter_returns_models() -> None:
    column = ColumnModel.from_dict({"name": "country", "type": "fixed", "value": "USA"})

    assert column == ColumnModel(name="country", type="fixed", value="USA")


def test_generator_config_reads_destinations() -> None:
    config = ConfigModel.from_dict(
        {
            "row_count": 1,
            "output_name": "x",
            "kafka_topic": "test-events",
            "kafka_key_column": "country",
            "destinations": ["csv", "json", "database"],
            "columns": [{"name": "country", "type": "fixed", "value": "USA"}],
        }
    )

    assert config.destinations == ("csv", "json", "database")


def test_generator_config_reads_kafka_key_column() -> None:
    config = ConfigModel.from_dict(
        {
            "row_count": 1,
            "output_name": "x",
            "kafka_topic": "test-events",
            "kafka_key_column": "record_id",
            "destinations": ["kafka"],
            "columns": [{"name": "record_id", "type": "sequence", "start": 1, "step": 1}],
        }
    )

    assert config.kafka_key_column == "record_id"
def test_load_config_reports_missing_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CONFIG_DIR", str(tmp_path))
    importlib.reload(env_config)
    try:
        with pytest.raises(Exception):
            ConfigModel.from_file("config_absent.json")
    finally:
        monkeypatch.delenv("CONFIG_DIR", raising=False)
        importlib.reload(env_config)


def test_load_config_reports_invalid_json(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "config_broken.json"
    path.write_text("{not json", encoding="utf-8")
    monkeypatch.setenv("CONFIG_DIR", str(tmp_path))
    importlib.reload(env_config)
    try:
        with pytest.raises(Exception):
            ConfigModel.from_file("config_broken.json")
    finally:
        monkeypatch.delenv("CONFIG_DIR", raising=False)
        importlib.reload(env_config)


def test_load_config_reports_non_object_json(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "config_list.json"
    path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    monkeypatch.setenv("CONFIG_DIR", str(tmp_path))
    importlib.reload(env_config)
    try:
        with pytest.raises(TypeError):
            ConfigModel.from_file("config_list.json")
    finally:
        monkeypatch.delenv("CONFIG_DIR", raising=False)
        importlib.reload(env_config)


def test_online_shopping_config_includes_extended_fields() -> None:
    config = ConfigModel.from_file("online_shopping.json")

    assert config.destinations == ("csv", "json", "database", "kafka")
    assert "subtotal" in config.column_names
    assert "discount_percent" in config.column_names
    assert "shipping_cost" in config.column_names
    assert "tax_amount" in config.column_names
    assert "total_amount" in config.column_names
    assert "payment_status" in config.column_names
    assert "fulfillment_status" in config.column_names
    assert "estimated_delivery_date" in config.column_names


def test_read_config_resolves_dataset_name_without_json_suffix() -> None:
    config = ConfigModel.from_file("online_shopping")

    assert config.output_name == "online_shopping"


def test_load_config_accepts_name_without_extension(project_root: Path) -> None:
    assert ConfigModel.from_file("demo").name == "demo.json"


def test_load_config_accepts_path_outside_config_dir(tmp_path: Path) -> None:
    path = tmp_path / "custom.json"
    path.write_text(json.dumps({
        "row_count": 1,
        "output_name": "custom",
        "kafka_topic": "test-events",
        "kafka_key_column": "id",
        "destinations": ["csv"],
        "columns": [{"name": "id", "type": "sequence"}],
    }), encoding="utf-8")

    config = ConfigModel.from_file(path)

    assert config.name == "custom.json"
    assert config.output_name == "custom"


def test_dataset_metadata_from_dataset(project_root: Path) -> None:
    metadata = DatasetMetadata.from_dataset(Dataset(name="demo", config=ConfigModel.from_file("demo.json")))

    assert metadata.name == "demo"
    assert metadata.config_file == "config/demo.json"
    assert metadata.file == "output_test/demo.csv"
    assert metadata.download_url == "/datasets/demo/download"
    assert metadata.row_count == 5
