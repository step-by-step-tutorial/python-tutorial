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
