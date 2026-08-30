import csv
import json
from datetime import datetime
from pathlib import Path

from ml_prediction.evaluation.model_evaluator import RegressionMetrics
from ml_prediction.model.experiment_result import ExperimentResult


class ExperimentRepository:
    fieldnames = (
        "experiment_id",
        "timestamp",
        "dataset_name",
        "model_type",
        "model_parameters",
        "baseline_validation_mae",
        "baseline_validation_rmse",
        "baseline_validation_r2",
        "validation_mae",
        "validation_rmse",
        "validation_r2",
        "test_mae",
        "test_rmse",
        "test_r2",
        "model_path",
        "report_path",
    )

    def __init__(self, path: Path) -> None:
        self.path = path

    def save(self, result: ExperimentResult) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        write_header = not self.path.exists() or self.path.stat().st_size == 0
        with self.path.open("a", newline="", encoding="utf-8") as history_file:
            writer = csv.DictWriter(history_file, fieldnames=self.fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerow(self._to_row(result))

    def read_all(self, dataset_name: str | None = None) -> list[ExperimentResult]:
        if not self.path.exists():
            return []
        with self.path.open(newline="", encoding="utf-8") as history_file:
            rows = csv.DictReader(history_file)
            return [
                self._from_row(row)
                for row in rows
                if dataset_name is None or row["dataset_name"] == dataset_name
            ]

    @staticmethod
    def _to_row(result: ExperimentResult) -> dict[str, str]:
        return {
            "experiment_id": result.experiment_id,
            "timestamp": result.timestamp.isoformat(),
            "dataset_name": result.dataset_name,
            "model_type": result.model_type,
            "model_parameters": json.dumps(result.model_parameters, sort_keys=True, separators=(",", ":")),
            "baseline_validation_mae": str(result.baseline_validation_metrics.mean_absolute_error),
            "baseline_validation_rmse": str(result.baseline_validation_metrics.root_mean_squared_error),
            "baseline_validation_r2": str(result.baseline_validation_metrics.r2_score),
            "validation_mae": str(result.validation_metrics.mean_absolute_error),
            "validation_rmse": str(result.validation_metrics.root_mean_squared_error),
            "validation_r2": str(result.validation_metrics.r2_score),
            "test_mae": str(result.test_metrics.mean_absolute_error),
            "test_rmse": str(result.test_metrics.root_mean_squared_error),
            "test_r2": str(result.test_metrics.r2_score),
            "model_path": str(result.model_path),
            "report_path": str(result.report_path) if result.report_path is not None else "",
        }

    @staticmethod
    def _from_row(row: dict[str, str]) -> ExperimentResult:
        return ExperimentResult(
            experiment_id=row["experiment_id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            dataset_name=row["dataset_name"],
            model_type=row["model_type"],
            model_parameters=json.loads(row["model_parameters"]),
            baseline_validation_metrics=RegressionMetrics(
                mean_absolute_error=float(row["baseline_validation_mae"]),
                root_mean_squared_error=float(row["baseline_validation_rmse"]),
                r2_score=float(row["baseline_validation_r2"]),
            ),
            validation_metrics=RegressionMetrics(
                mean_absolute_error=float(row["validation_mae"]),
                root_mean_squared_error=float(row["validation_rmse"]),
                r2_score=float(row["validation_r2"]),
            ),
            test_metrics=RegressionMetrics(
                mean_absolute_error=float(row["test_mae"]),
                root_mean_squared_error=float(row["test_rmse"]),
                r2_score=float(row["test_r2"]),
            ),
            model_path=Path(row["model_path"]),
            report_path=Path(row["report_path"]) if row["report_path"] else None,
        )
