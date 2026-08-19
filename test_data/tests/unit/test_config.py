

import json
from pathlib import Path

import pytest

from application_config import ColumnConfig, load_config, GeneratorConfig
from exceptions import ConfigurationError


def test_load_config_reads_columns_and_seed(project_root: Path) -> None:
    config = load_config(project_root / "config_demo.json")

    assert config.row_count == 5
    assert config.seed == 42
    assert config.output_file == "output/demo.csv"
    assert config.headers == ("order_id", "customer_name", "product_name", "category", "country")


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
                "output_file": "output/x.csv",
                "columns": [
                    {"name": "country", "type": "fixed", "value": "Germany"},
                    {"name": "country", "type": "fixed", "value": "USA"},
                ],
            }
        )


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ({"output_file": "o.csv", "columns": []}, "missing the 'row_count' key"),
        ({"row_count": 1, "columns": []}, "missing the 'output_file' key"),
        ({"row_count": 1, "output_file": "o.csv"}, "missing the 'columns' key"),
        ({"row_count": -1, "output_file": "o.csv", "columns": [{}]}, "non-negative integer"),
        ({"row_count": 1, "output_file": "o.csv", "columns": []}, "non-empty list"),
    ],
)
def test_generator_config_rejects_bad_top_level_keys(raw: dict, message: str) -> None:
    with pytest.raises(ConfigurationError, match=message):
        GeneratorConfig.from_dict(raw)


def test_load_config_reports_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigurationError, match="Config file not found"):
        load_config(tmp_path / "config_absent.json")


def test_load_config_reports_invalid_json(tmp_path: Path) -> None:
    path = tmp_path / "config_broken.json"
    path.write_text("{not json", encoding="utf-8")

    with pytest.raises(ConfigurationError, match="not valid JSON"):
        load_config(path)


def test_load_config_reports_non_object_json(tmp_path: Path) -> None:
    path = tmp_path / "config_list.json"
    path.write_text(json.dumps([1, 2, 3]), encoding="utf-8")

    with pytest.raises(ConfigurationError, match="must hold a JSON object"):
        load_config(path)
