from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pyarrow.compute as pc
import pyarrow.parquet as pq


def read_column_names(path: Path) -> list[str]:
    return pq.ParquetFile(path).schema_arrow.names


def read_rows(
        path: Path,
        columns: list[str],
        batch_size: int,
        where: dict[str, Any] | None = None,
) -> Iterator[dict[str, Any]]:
    """Yield rows of the given columns in batches, keeping only rows whose columns equal the where values.

    Filtering runs in Arrow before rows become Python objects, so skipped rows cost almost nothing.
    """
    for batch in pq.ParquetFile(path).iter_batches(batch_size=batch_size, columns=columns):
        for column, value in (where or {}).items():
            batch = batch.filter(pc.equal(batch.column(column), value))

        yield from batch.to_pylist()
