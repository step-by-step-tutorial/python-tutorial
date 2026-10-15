import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from shapely.geometry import Point


def geoname_line(geoname_id: str, name: str, feature_class: str, state_code: str, population: int) -> str:
    values = [""] * 19
    values[0] = geoname_id
    values[1] = name
    values[2] = name
    values[6] = feature_class
    values[8] = "US"
    values[10] = state_code
    values[14] = str(population)
    values[17] = "America/Los_Angeles"
    return "\t".join(values)


def postal_code_line(postal_code: str, city: str) -> str:
    return "\t".join(["US", postal_code, city, "California", "CA", "", "", "", "", "34.05", "-118.24", "4"])


def address(address_id: str, country: str, state: str, city: str | None = None, postcode: str | None = None,
            geometry: bytes | None = None) -> dict:
    return {
        "id": address_id,
        "geometry": geometry if geometry is not None else Point(-118.24, 34.05).wkb,
        "country": country,
        "postcode": postcode,
        "street": "Main Street",
        "number": "1",
        "unit": None,
        "postal_city": city,
        "address_levels": [{"value": state}],
    }


ADDRESS_SCHEMA = pa.schema([
    ("id", pa.string()),
    ("geometry", pa.binary()),
    ("country", pa.string()),
    ("postcode", pa.string()),
    ("street", pa.string()),
    ("number", pa.string()),
    ("unit", pa.string()),
    ("postal_city", pa.string()),
    ("address_levels", pa.list_(pa.struct([("value", pa.string())]))),
    ("ignored_column", pa.string()),
])


@pytest.fixture
def project_dir(tmp_path: Path) -> Path:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "allCountries.txt").write_text("\n".join([
        # A park listed before the city must not win the "los angeles" name.
        geoname_line("1", "Los Angeles", "L", "CA", 0),
        geoname_line("5368361", "Los Angeles", "P", "CA", 3820914),
        geoname_line("2", "Los Angeles", "P", "CA", 100),
        geoname_line("3", "Los Angeles", "P", "TX", 99999999),
    ]) + "\n", encoding="utf-8")
    (data_dir / "postalCodes_allCountries.txt").write_text(
        postal_code_line("90049", "Los Angeles") + "\n", encoding="utf-8"
    )

    rows = [
        address("a1", "US", "CA", city="Los Angeles"),
        address("a2", "US", "CA", postcode="90049"),
        address("a3", "US", "CA", city="San Diego"),
        address("a4", "US", "NV", city="Los Angeles"),
        address("a5", "MX", "CA", city="Los Angeles"),
        address("a6", "US", "California", city="los  angeles", geometry=b"not-wkb"),
    ]
    for row in rows:
        row["ignored_column"] = "x"
    pq.write_table(pa.Table.from_pylist(rows, schema=ADDRESS_SCHEMA), data_dir / "addresses.parquet")

    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "targets.json").write_text(json.dumps({
        "geonames_file": "../data/allCountries.txt",
        "postal_codes_file": "../data/postalCodes_allCountries.txt",
        "output_dir": "../output",
        "targets": [
            {
                "country_code": "US",
                "country": "United States",
                "state_code": "CA",
                "state": "California",
                "cities": ["Los Angeles"],
                "input_file": "../data/addresses.parquet",
                "output_file": "los_angeles.csv",
            },
            {
                "country_code": "US",
                "country": "United States",
                "state_code": "NY",
                "state": "New York",
                "cities": ["new york"],
                "input_file": "../data/missing.parquet",
                "output_file": "new_york.csv",
            },
        ],
    }), encoding="utf-8")
    return tmp_path
