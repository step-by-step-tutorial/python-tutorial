"""CSV export.

Kept apart from row generation so rows can be streamed straight to disk: the writer
consumes any iterable, so nothing forces a whole dataset into memory.
"""


import csv
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Mapping


def write_rows(
    output_path: Path,
    headers: Sequence[str],
    rows: Iterable[Mapping[str, str]],
) -> int:
    """Write ``rows`` as a CSV with a header line, creating parent folders.

    Returns:
        The number of data rows written, header excluded.
    """
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(headers))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
            written += 1

    return written
