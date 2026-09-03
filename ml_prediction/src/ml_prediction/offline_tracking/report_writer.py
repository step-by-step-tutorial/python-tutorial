import csv
import hashlib
import json
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ml_prediction.offline_tracking.models import ReportEvent


class ReportWriter:
    fieldnames = tuple(ReportEvent.__dataclass_fields__)

    def __init__(self, path: Path, dataset_name: str, operation: str, model_path: Path | None = None, run_id: str = "") -> None:
        self.path = path
        self.dataset = dataset_name
        self.operation = operation
        self.model_path = model_path
        self.run_id = run_id
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", newline="", encoding="utf-8") as report_file:
            csv.DictWriter(report_file, fieldnames=self.fieldnames).writeheader()

    def record(self, step: str, partition: str = "", rows: int | None = None, model_name: str = "", model_path: Path | None = None, metrics: Any = None, details: str = "") -> None:
        selected_path = model_path if isinstance(model_path, Path) else self.model_path
        metric_values = asdict(metrics) if metrics is not None and is_dataclass(metrics) else metrics
        event = ReportEvent(
            datetime.now(timezone.utc), self.run_id, self.dataset, self.operation, step,
            partition, rows, model_name, str(selected_path or ""), self.model_id(selected_path),
            metric_values, details,
        )
        row = asdict(event)
        row["timestamp"] = event.timestamp.isoformat()
        row["metrics"] = json.dumps(event.metrics or {}, sort_keys=True, separators=(",", ":"))
        with self.path.open("a", newline="", encoding="utf-8") as report_file:
            csv.DictWriter(report_file, fieldnames=self.fieldnames).writerow(row)

    @staticmethod
    def model_id(model_path: Path | None) -> str:
        if not isinstance(model_path, Path) or not model_path.exists():
            return ""
        digest = hashlib.sha256()
        with model_path.open("rb") as model_file:
            for chunk in iter(lambda: model_file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
