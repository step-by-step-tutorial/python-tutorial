

import json
import importlib
from pathlib import Path

import pytest
import env_config

from config_utils import (
    convert_to_column,
    convert_to_columns,
    convert_to_config,
    read_config,
)
from schemas import ColumnModel


def test_load_config_reads_columns(project_root: Path) -> None:
    config = read_config("demo.json")

    assert config.row_count == 5
    assert config.output_file == "demo.csv"
    assert config.headers == ("order_id", "customer_name", "product_name", "category", "country")
    assert config.destinations == ("csv",)


def test_column_config_converts_file_columns_to_tuple() -> None:
    column = convert_to_column(
        {
            "name": "customer_name",
            "type": "random_from_mapped_file",
            "file_columns": ["first_name_file", "last_name_file"],
        }
    )

    assert column.file_columns == ("first_name_file", "last_name_file")


def test_column_model_list_converter_returns_models() -> None:
    columns = convert_to_columns(
        [{"name": "country", "type": "fixed", "value": "USA"}]
    )

    assert columns == (ColumnModel(name="country", type="fixed", value="USA"),)


def test_generator_config_reads_destinations() -> None:
    config = convert_to_config(
        {
            "row_count": 1,
            "output_file": "x.csv",
            "destinations": ["csv", "json", "database"],
            "columns": [{"name": "country", "type": "fixed", "value": "USA"}],
        }
    )

    assert config.destinations == ("csv", "json", "database")


def test_load_config_reports_missing_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CONFIG_DIR", str(tmp_path))
    importlib.reload(env_config)
    try:
        with pytest.raises(Exception):
            read_config("config_absent.json")
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
            read_config("config_broken.json")
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
            read_config("config_list.json")
    finally:
        monkeypatch.delenv("CONFIG_DIR", raising=False)
        importlib.reload(env_config)


def test_online_shopping_config_includes_extended_fields() -> None:
    config = read_config("online_shopping.json")

    assert config.destinations == ("csv", "json", "database")
    assert "subtotal" in config.headers
    assert "discount_percent" in config.headers
    assert "shipping_cost" in config.headers
    assert "tax_amount" in config.headers
    assert "total_amount" in config.headers
    assert "payment_status" in config.headers
    assert "fulfillment_status" in config.headers
    assert "estimated_delivery_date" in config.headers
