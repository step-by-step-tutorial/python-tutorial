import csv
import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from ml_prediction.evaluation.model_evaluator import RegressionMetrics


@dataclass
class Report:
    path: Path
    dataset: str

    fieldnames = (
        "timestamp",
        "dataset",
        "operation",
        "step",
        "partition",
        "rows",
        "model",
        "model_path",
        "model_id",
        "mae",
        "rmse",
        "r2",
        "details",
    )

    def __init__(self, path: Path, dataset: str, operation: str, model_path: Path | None = None) -> None:
        self.path = path
        self.dataset = dataset
        self.operation = operation
        self.model_path = model_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", newline="", encoding="utf-8") as report_file:
            csv.DictWriter(report_file, fieldnames=self.fieldnames).writeheader()

    def record(
            self,
            step: str,
            partition: str = "",
            rows: int | None = None,
            model_name: str = "",
            model_path: Path | None = None,
            metrics: RegressionMetrics | None = None,
            details: str = "",
    ) -> None:
        selected_model_path = model_path if isinstance(model_path, Path) else self.model_path
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dataset": self.dataset,
            "operation": self.operation,
            "step": step,
            "partition": partition,
            "rows": rows if rows is not None else "",
            "model": model_name,
            "model_path": selected_model_path or "",
            "model_id": self.model_id(selected_model_path),
            "mae": metrics.mean_absolute_error if metrics else "",
            "rmse": metrics.root_mean_squared_error if metrics else "",
            "r2": metrics.r2_score if metrics else "",
            "details": details,
        }
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


class ReportService:
    """Create and format CSV reports from workflow events and supplied metrics."""

    def __init__(self, report_dir: Path) -> None:
        self.report_dir = report_dir

    def start(self, dataset: str, operation: str, model_path: Path | None = None) -> Report:
        """Create a report file; callers remain responsible for all calculations and persistence."""
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        path = self.report_dir / f"{dataset}_{operation}_report_{timestamp}.csv"
        return Report(path, dataset, operation, model_path)
