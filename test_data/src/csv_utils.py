from __future__ import annotations

import csv
from pathlib import Path


def count_rows(path: Path) -> int:
    with Path(path).open("r", encoding="utf-8", newline="") as file:
        return max(sum(1 for _ in csv.reader(file)) - 1, 0)
