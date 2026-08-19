

import json
from pathlib import Path

import pytest


def write_lines(path: Path, *lines: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


@pytest.fixture(name="write_lines")
def write_lines_fixture():
    return write_lines


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    data = tmp_path / "data"
    data.mkdir()
    return data


@pytest.fixture
def project_root(tmp_path: Path, data_dir: Path) -> Path:
    write_lines(data_dir / "countries.txt", "Germany", "USA")
    write_lines(data_dir / "first_names" / "germany.txt", "Hans")
    write_lines(data_dir / "first_names" / "usa.txt", "John")
    write_lines(data_dir / "last_names" / "germany.txt", "Bauer")
    write_lines(data_dir / "last_names" / "usa.txt", "Smith")
    write_lines(
        data_dir / "country_source_map.csv",
        "country,first_name_file,last_name_file",
        "Germany,data/first_names/germany.txt,data/last_names/germany.txt",
        "USA,data/first_names/usa.txt,data/last_names/usa.txt",
    )
    write_lines(data_dir / "product_names.txt", "Laptop", "Desk")
    write_lines(
        data_dir / "product_catalog.csv",
        "product,category,unit_price",
        "Laptop,Electronics,1200",
        "Desk,Furniture,300",
    )

    config = {
        "row_count": 5,
        "output_file": "output/demo.csv",
        "seed": 42,
        "columns": [
            {"name": "order_id", "type": "sequence", "start": 1, "step": 1},
            {
                "name": "customer_name",
                "type": "random_from_mapped_file",
                "source_field": "country",
                "mapping_file": "data/country_source_map.csv",
                "key_column": "country",
                "file_columns": ["first_name_file", "last_name_file"],
                "separator": " ",
            },
            {"name": "product_name", "type": "random_from_file", "file": "data/product_names.txt"},
            {
                "name": "category",
                "type": "derived",
                "method": "lookup_from_csv",
                "source_field": "product_name",
                "mapping_file": "data/product_catalog.csv",
                "key_column": "product",
                "value_column": "category",
            },
            {"name": "country", "type": "random_from_file", "file": "data/countries.txt"},
        ],
    }
    (tmp_path / "config_demo.json").write_text(json.dumps(config), encoding="utf-8")
    return tmp_path
