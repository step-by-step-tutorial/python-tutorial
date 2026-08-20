

import json
import importlib
from pathlib import Path

import pytest
import env_config

from application_config import ColumnConfig, load_config, GeneratorConfig
from exceptions import ConfigurationError


def test_load_config_reads_columns_and_seed(project_root: Path) -> None:
    config = load_config("demo.json")

    assert config.row_count == 5
    assert config.seed == 42
    assert config.output_file == "demo.csv"
    assert config.headers == ("order_id", "customer_name", "product_name", "category", "country")
    assert config.destinations == ("csv",)


def test_column_config_converts_file_columns_to_tuple() -> None:
    column = ColumnConfig.from_dict(
        {
            "name": "customer_name",
            "type": "random_from_mapped_file",
            "file_columns": ["first_name_file", "last_name_file"],
        }
    )

    assert column.file_columns == ("first_name_file", "last_name_file")


def test_column_config_rejects_unknown_keys() -> None:
    with pytest.raises(ConfigurationError, match="unknown keys: fille"):
        ColumnConfig.from_dict({"name": "country", "type": "random_from_file", "fille": "x.txt"})


def test_column_config_requires_name_and_type() -> None:
    with pytest.raises(ConfigurationError, match="needs a 'type'"):
        ColumnConfig.from_dict({"name": "country"})


def test_generator_config_rejects_duplicate_column_names() -> None:
    with pytest.raises(ConfigurationError, match="Duplicate column names: country"):
        GeneratorConfig.from_dict(
            {
                "row_count": 1,
                "output_file": "x.csv",
                "destinations": ["csv"],
                "columns": [
                    {"name": "country", "type": "fixed", "value": "Germany"},
                    {"name": "country", "type": "fixed", "value": "USA"},
                ],
            }
        )


def test_generator_config_reads_destinations() -> None:
    config = GeneratorConfig.from_dict(
        {
            "row_count": 1,
            "output_file": "x.csv",
            "destinations": ["csv", "json", "database"],
            "columns": [{"name": "country", "type": "fixed", "value": "USA"}],
        }
    )

    assert config.destinations == ("csv", "json", "database")


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ({"output_file": "o.csv", "columns": [], "destinations": ["csv"]}, "missing the 'row_count' key"),
        ({"row_count": 1, "columns": [], "destinations": ["csv"]}, "missing the 'output_file' key"),
        ({"row_count": 1, "output_file": "o.csv", "destinations": ["csv"]}, "missing the 'columns' key"),
        ({"row_count": -1, "output_file": "o.csv", "columns": [{}], "destinations": ["csv"]}, "non-negative integer"),
        ({"row_count": 1, "output_file": "o.csv", "columns": [], "destinations": ["csv"]}, "non-empty list"),
    ],
)
def test_generator_config_rejects_bad_top_level_keys(raw: dict, message: str) -> None:
    with pytest.raises(ConfigurationError, match=message):
        GeneratorConfig.from_dict(raw)


def test_generator_config_requires_destinations() -> None:
    with pytest.raises(ConfigurationError, match="missing the 'destinations' key"):
        GeneratorConfig.from_dict(
            {
                "row_count": 1,
                "output_file": "o.csv",
                "columns": [{"name": "country", "type": "fixed", "value": "USA"}],
            }
        )


def test_load_config_reports_missing_file(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("CONFIG_DIR", str(tmp_path))
    importlib.reload(env_config)

    with pytest.raises(ConfigurationError, match="Reading JSON file"):
        load_config("config_absent.json")

    monkeypatch.delenv("CONFIG_DIR", raising=False)
    importlib.reload(env_config)


def test_load_config_reports_invalid_json(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "config_broken.json"
    path.write_text("{not json", encoding="utf-8")
    monkeypatch.setenv("CONFIG_DIR", str(tmp_path))
    importlib.reload(env_config)

    with pytest.raises(ConfigurationError, match="Reading JSON file"):
        load_config("config_broken.json")

    monkeypatch.delenv("CONFIG_DIR", raising=False)
    importlib.reload(env_config)


def test_load_config_reports_non_object_json(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / "config_list.json"
    path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    monkeypatch.setenv("CONFIG_DIR", str(tmp_path))
    importlib.reload(env_config)

    with pytest.raises(ConfigurationError, match="Reading JSON file"):
        load_config("config_list.json")

    monkeypatch.delenv("CONFIG_DIR", raising=False)
    importlib.reload(env_config)


def test_online_shopping_config_includes_extended_fields() -> None:
    config = load_config("online_shopping.json")

    assert config.destinations == ("csv", "json", "database")
    assert "subtotal" in config.headers
    assert "discount_percent" in config.headers
    assert "shipping_cost" in config.headers
    assert "tax_amount" in config.headers
    assert "total_amount" in config.headers
    assert "payment_status" in config.headers
    assert "fulfillment_status" in config.headers
    assert "estimated_delivery_date" in config.headers
