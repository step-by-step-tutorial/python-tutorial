import json
import importlib
from dataclasses import asdict
from pathlib import Path

import pytest
import env_config

from data_converter import convert_to_email
from dataset_generator import DatasetGenerator
from schemas import ColumnModel, ConfigModel


@pytest.fixture(autouse=True)
def temp_project_env(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("PROJECT_ROOT", str(tmp_path))
    monkeypatch.setenv("CONFIG_DIR", str(tmp_path / "config"))
    monkeypatch.setenv("OUTPUT_DIR", str(tmp_path / "output"))
    importlib.reload(env_config)
    yield
    importlib.reload(env_config)


def write_config_file(tmp_path: Path, name: str, config: ConfigModel) -> str:
    config_dir = tmp_path / "config"
    config_dir.mkdir(exist_ok=True)
    (config_dir / name).write_text(json.dumps(asdict(config)), encoding="utf-8")
    return name


def config_with_headers(**kwargs) -> ConfigModel:
    return ConfigModel(column_names=tuple(column.name for column in kwargs["columns"]), **kwargs)


def test_normalize_for_email_removes_special_characters() -> None:
    assert convert_to_email("Emily Johnson") == "emily.johnson"
    assert convert_to_email("Alyssa") == "alyssa"


def test_generate_rows_creates_derived_email(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "first_names.txt").write_text("John\n", encoding="utf-8")
    (data_dir / "last_names.txt").write_text("Smith\n", encoding="utf-8")

    config = config_with_headers(
        row_count=1,
        output_file="generated.csv",
        destinations=("csv",),
        columns=[
            ColumnModel(name="first_name", type="random_from_file", file="data/first_names.txt"),
            ColumnModel(name="last_name", type="random_from_file", file="data/last_names.txt"),
            ColumnModel(
                name="email",
                type="derived",
                method="email_from_source_fields",
                source_fields=("first_name", "last_name"),
                domain="example.com",
            ),
        ],
    )

    generator = DatasetGenerator(write_config_file(tmp_path, "generated.json", config))
    rows = list(generator.generate_rows())

    assert rows == [
        {
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@example.com",
        }
    ]


def test_generate_rows_supports_sequence_random_int_and_lookup(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "products.txt").write_text("Laptop\n", encoding="utf-8")
    (data_dir / "product_catalog.csv").write_text(
        "product,category,unit_price\nLaptop,Electronics,1200\n",
        encoding="utf-8",
    )

    config = config_with_headers(
        row_count=1,
        output_file="generated.csv",
        destinations=("csv",),
        columns=[
            ColumnModel(name="order_id", type="sequence", start=1, step=1),
            ColumnModel(name="product", type="random_from_file", file="data/products.txt"),
            ColumnModel(
                name="category",
                type="derived",
                method="lookup_from_csv",
                source_field="product",
                mapping_file="data/product_catalog.csv",
                key_column="product",
                value_column="category",
            ),
            ColumnModel(
                name="unit_price",
                type="derived",
                method="lookup_from_csv",
                source_field="product",
                mapping_file="data/product_catalog.csv",
                key_column="product",
                value_column="unit_price",
            ),
            ColumnModel(name="quantity", type="random_int", min=1, max=5),
            ColumnModel(
                name="order_date",
                type="random_date",
                date_start="2026-01-01",
                date_end="2026-01-31",
            ),
        ],
    )

    generator = DatasetGenerator(write_config_file(tmp_path, "generated.json", config))
    rows = list(generator.generate_rows())

    assert rows[0]["order_id"] == "1"
    assert rows[0]["product"] == "Laptop"
    assert rows[0]["category"] == "Electronics"
    assert rows[0]["unit_price"] == "1200"
    assert 1 <= int(rows[0]["quantity"]) <= 5
    assert rows[0]["order_date"].startswith("2026-01-")


def test_product_of_fields_can_use_custom_source_fields(tmp_path: Path) -> None:
    config = config_with_headers(
        row_count=1,
        output_file="generated.csv",
        destinations=("csv",),
        columns=[
            ColumnModel(name="qty", type="fixed", value="2"),
            ColumnModel(name="price", type="fixed", value="10"),
            ColumnModel(
                name="line_total",
                type="derived",
                method="product_of_source_fields",
                source_fields=("qty", "price"),
            ),
        ],
    )

    generator = DatasetGenerator(write_config_file(tmp_path, "generated.json", config))
    rows = list(generator.generate_rows())

    assert rows == [{"qty": "2", "price": "10", "line_total": "20.0"}]


def test_product_of_source_fields_can_use_a_constant_factor(tmp_path: Path) -> None:
    config = config_with_headers(
        row_count=1,
        output_file="generated.csv",
        destinations=("csv",),
        columns=[
            ColumnModel(name="net_total", type="fixed", value="25"),
            ColumnModel(
                name="vat_amount",
                type="derived",
                method="product_of_source_fields",
                source_fields=("net_total",),
                value=0.2,
            ),
        ],
    )

    generator = DatasetGenerator(write_config_file(tmp_path, "generated.json", config))
    rows = list(generator.generate_rows())

    assert rows == [{"net_total": "25", "vat_amount": "5.0"}]


def test_product_of_source_fields_supports_a_zero_constant_factor(tmp_path: Path) -> None:
    config = config_with_headers(
        row_count=1,
        output_file="generated.csv",
        destinations=("csv",),
        columns=[
            ColumnModel(name="net_total", type="fixed", value="25"),
            ColumnModel(
                name="vat_amount",
                type="derived",
                method="product_of_source_fields",
                source_fields=("net_total",),
                value=0.0,
            ),
        ],
    )

    generator = DatasetGenerator(write_config_file(tmp_path, "generated.json", config))
    rows = list(generator.generate_rows())

    assert rows == [{"net_total": "25", "vat_amount": "0.0"}]


def test_generate_rows_supports_random_from_mapped_file(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    names_dir = data_dir / "names"
    names_dir.mkdir(parents=True)
    (names_dir / "germany.txt").write_text("Hans\n", encoding="utf-8")
    (names_dir / "usa.txt").write_text("John\n", encoding="utf-8")
    (data_dir / "country_source_map.csv").write_text(
        "country,name_file\nGermany,data/names/germany.txt\nUSA,data/names/usa.txt\n",
        encoding="utf-8",
    )

    config = config_with_headers(
        row_count=1,
        output_file="generated.csv",
        destinations=("csv",),
        columns=[
            ColumnModel(name="country", type="fixed", value="Germany"),
            ColumnModel(
                name="customer_name",
                type="random_from_mapped_file",
                source_field="country",
                mapping_file="data/country_source_map.csv",
                key_column="country",
                file_column="name_file",
            ),
        ],
    )

    generator = DatasetGenerator(write_config_file(tmp_path, "generated.json", config))
    rows = list(generator.generate_rows())

    assert rows == [{"country": "Germany", "customer_name": "Hans"}]


def test_random_from_mapped_file_joins_multiple_file_columns(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    names_dir = data_dir / "names"
    names_dir.mkdir(parents=True)
    (names_dir / "germany_first.txt").write_text("Hans\n", encoding="utf-8")
    (names_dir / "germany_last.txt").write_text("Bauer\n", encoding="utf-8")
    (data_dir / "country_source_map.csv").write_text(
        "country,first_name_file,last_name_file\n"
        "Germany,data/names/germany_first.txt,data/names/germany_last.txt\n",
        encoding="utf-8",
    )

    config = config_with_headers(
        row_count=1,
        output_file="generated.csv",
        destinations=("csv",),
        columns=[
            ColumnModel(name="country", type="fixed", value="Germany"),
            ColumnModel(
                name="customer_name",
                type="random_from_mapped_file",
                source_field="country",
                mapping_file="data/country_source_map.csv",
                key_column="country",
                file_columns=["first_name_file", "last_name_file"],
                separator=" ",
            ),
        ],
    )

    generator = DatasetGenerator(write_config_file(tmp_path, "generated.json", config))
    rows = list(generator.generate_rows())

    assert rows == [{"country": "Germany", "customer_name": "Hans Bauer"}]


def test_generate_rows_resolves_column_listed_after_its_dependents(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    names_dir = data_dir / "names"
    names_dir.mkdir(parents=True)
    (names_dir / "germany.txt").write_text("Hans\n", encoding="utf-8")
    (data_dir / "countries.txt").write_text("Germany\n", encoding="utf-8")
    (data_dir / "country_source_map.csv").write_text(
        "country,name_file\nGermany,data/names/germany.txt\n",
        encoding="utf-8",
    )

    config = config_with_headers(
        row_count=1,
        output_file="generated.csv",
        destinations=("csv",),
        columns=[
            ColumnModel(
                name="customer_name",
                type="random_from_mapped_file",
                source_field="country",
                mapping_file="data/country_source_map.csv",
                key_column="country",
                file_column="name_file",
            ),
            ColumnModel(name="country", type="random_from_file", file="data/countries.txt"),
        ],
    )

    generator = DatasetGenerator(write_config_file(tmp_path, "generated.json", config))
    rows = list(generator.generate_rows())

    assert list(rows[0]) == ["customer_name", "country"]
    assert rows[0] == {"customer_name": "Hans", "country": "Germany"}


def test_generate_rows_rejects_circular_dependencies(tmp_path: Path) -> None:
    config = config_with_headers(
        row_count=1,
        output_file="generated.csv",
        destinations=("csv",),
        columns=[
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

    with pytest.raises(Exception):
        DatasetGenerator(write_config_file(tmp_path, "generated.json", config))


