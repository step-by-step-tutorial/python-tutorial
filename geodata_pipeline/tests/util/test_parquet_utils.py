from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from geodata_pipeline.util.parquet_utils import read_column_names, read_rows


def write_parquet(path: Path) -> None:
    pq.write_table(pa.table({"id": ["1", "2", "3"], "country": ["US", "MX", "US"], "other": ["x", "y", "z"]}), path)


def test_read_column_names(tmp_path: Path) -> None:
    path = tmp_path / "file.parquet"
    write_parquet(path)

    assert read_column_names(path) == ["id", "country", "other"]


def test_read_rows_selects_columns_and_filters_across_batches(tmp_path: Path) -> None:
    path = tmp_path / "file.parquet"
    write_parquet(path)

    rows = list(read_rows(path, ["id", "country"], batch_size=1, where={"country": "US"}))

    assert rows == [{"id": "1", "country": "US"}, {"id": "3", "country": "US"}]
