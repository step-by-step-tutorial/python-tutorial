import csv
from pathlib import Path

from geodata_pipeline.cli import main
from geodata_pipeline.model import AddressRecord


def read_output(project_dir: Path) -> list[dict[str, str]]:
    with (project_dir / "output" / "los_angeles.csv").open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def test_pipeline_writes_addresses_of_target_city(project_dir: Path) -> None:
    assert main(["--config", str(project_dir / "config" / "targets.json")]) == 0

    rows = read_output(project_dir)

    assert [row["overture_id"] for row in rows] == ["a1", "a2", "a6"]
    assert list(rows[0]) == AddressRecord.column_names()
    assert rows[0] == {
        "country": "United States",
        "country_code": "US",
        "state": "California",
        "state_code": "CA",
        "city": "Los Angeles",
        "postal_code": "",
        "street": "Main Street",
        "house_number": "1",
        "unit": "",
        "latitude": "34.05",
        "longitude": "-118.24",
        "geoname_id": "5368361",
        "timezone": "America/Los_Angeles",
        "population": "3820914",
        "overture_id": "a1",
    }


def test_pipeline_resolves_city_from_postal_code(project_dir: Path) -> None:
    main(["--config", str(project_dir / "config" / "targets.json")])

    row = read_output(project_dir)[1]

    assert row["city"] == "Los Angeles"
    assert row["postal_code"] == "90049"


def test_pipeline_keeps_rows_with_unreadable_geometry(project_dir: Path) -> None:
    main(["--config", str(project_dir / "config" / "targets.json")])

    row = read_output(project_dir)[2]

    assert row["latitude"] == ""
    assert row["longitude"] == ""


def test_pipeline_skips_targets_without_input_file(project_dir: Path) -> None:
    main(["--config", str(project_dir / "config" / "targets.json")])

    assert not (project_dir / "output" / "new_york.csv").exists()


def test_main_fails_when_geonames_files_are_missing(project_dir: Path) -> None:
    (project_dir / "data" / "allCountries.txt").unlink()

    assert main(["--config", str(project_dir / "config" / "targets.json")]) == 1
