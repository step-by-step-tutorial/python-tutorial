from pathlib import Path

from generator_service import normalize_for_email, GeneratorConfig, ColumnConfig, CsvDataGenerator


def test_normalize_for_email_removes_special_characters() -> None:
    assert normalize_for_email("Ali Reza") == "ali.reza"
    assert normalize_for_email("Jalalé") == "jalale"


def test_generate_rows_creates_derived_email(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "first_names.txt").write_text("John\n", encoding="utf-8")
    (data_dir / "last_names.txt").write_text("Smith\n", encoding="utf-8")

    config = GeneratorConfig(
        row_count=1,
        output_file="output/test.csv",
        seed=1,
        columns=[
            ColumnConfig(name="first_name", type="random_from_file", file="data/first_names.txt"),
            ColumnConfig(name="last_name", type="random_from_file", file="data/last_names.txt"),
            ColumnConfig(name="email", type="derived", method="email_from_name", domain="example.com"),
        ],
    )

    generator = CsvDataGenerator(config=config, project_root=tmp_path)
    rows = generator.generate_rows()

    assert rows == [
        {
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@example.com",
        }
    ]


def test_write_csv_writes_headers_and_rows(tmp_path: Path) -> None:
    config = GeneratorConfig(
        row_count=1,
        output_file="output/test.csv",
        columns=[ColumnConfig(name="country", type="fixed", value="Germany")],
    )
    generator = CsvDataGenerator(config=config, project_root=tmp_path)
    output_path = generator.write_csv([{"country": "Germany"}])

    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8").splitlines() == [
        "country",
        "Germany",
    ]


def test_generate_rows_supports_sequence_random_int_and_lookup(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "products.txt").write_text("Laptop\n", encoding="utf-8")
    (data_dir / "product_catalog.csv").write_text(
        "product,category,unit_price\nLaptop,Electronics,1200\n",
        encoding="utf-8",
    )

    config = GeneratorConfig(
        row_count=1,
        output_file="output/test.csv",
        seed=7,
        columns=[
            ColumnConfig(name="order_id", type="sequence", start=1, step=1),
            ColumnConfig(name="product", type="random_from_file", file="data/products.txt"),
            ColumnConfig(
                name="category",
                type="derived",
                method="lookup_from_csv",
                source_field="product",
                mapping_file="data/product_catalog.csv",
                key_column="product",
                value_column="category",
            ),
            ColumnConfig(
                name="unit_price",
                type="derived",
                method="lookup_from_csv",
                source_field="product",
                mapping_file="data/product_catalog.csv",
                key_column="product",
                value_column="unit_price",
            ),
            ColumnConfig(name="quantity", type="random_int", min=1, max=5),
            ColumnConfig(
                name="order_date",
                type="random_date",
                date_start="2026-01-01",
                date_end="2026-01-31",
            ),
        ],
    )

    generator = CsvDataGenerator(config=config, project_root=tmp_path)
    rows = generator.generate_rows()

    assert rows[0]["order_id"] == "1"
    assert rows[0]["product"] == "Laptop"
    assert rows[0]["category"] == "Electronics"
    assert rows[0]["unit_price"] == "1200"
    assert 1 <= int(rows[0]["quantity"]) <= 5
    assert rows[0]["order_date"].startswith("2026-01-")


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

    config = GeneratorConfig(
        row_count=1,
        output_file="output/test.csv",
        seed=1,
        columns=[
            ColumnConfig(name="country", type="fixed", value="Germany"),
            ColumnConfig(
                name="customer_name",
                type="random_from_mapped_file",
                source_field="country",
                mapping_file="data/country_source_map.csv",
                key_column="country",
                file_column="name_file",
            ),
        ],
    )

    generator = CsvDataGenerator(config=config, project_root=tmp_path)
    rows = generator.generate_rows()

    assert rows == [{"country": "Germany", "customer_name": "Hans"}]
