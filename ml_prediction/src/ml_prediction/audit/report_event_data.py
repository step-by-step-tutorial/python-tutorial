from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar

from ml_prediction.audit.models import Metrics


@dataclass(frozen=True)
class ReportEventData:
    step: ClassVar[str]

    def fields(self) -> dict[str, Any]:
        return {}


@dataclass(frozen=True)
class DatasetDownloaded(ReportEventData):
    dataset_path: Path
    step: ClassVar[str] = "dataset_downloaded"

    def fields(self) -> dict[str, Any]:
        return {"details": str(self.dataset_path)}


@dataclass(frozen=True)
class DatasetPrepared(ReportEventData):
    rows: int
    target_column: str
    step: ClassVar[str] = "dataset_prepared"

    def fields(self) -> dict[str, Any]:
        return {"rows": self.rows, "details": f"target={self.target_column}"}


@dataclass(frozen=True)
class FeaturesBuilt(ReportEventData):
    rows: int
    columns: int
    step: ClassVar[str] = "features_built"

    def fields(self) -> dict[str, Any]:
        return {"rows": self.rows, "details": f"columns={self.columns}"}


@dataclass(frozen=True)
class TargetExtracted(ReportEventData):
    rows: int
    target_column: str
    step: ClassVar[str] = "target_extracted"

    def fields(self) -> dict[str, Any]:
        return {"rows": self.rows, "details": f"column={self.target_column}"}


@dataclass(frozen=True)
class DatasetSplit(ReportEventData):
    rows: int
    train_rows: int
    validation_rows: int
    test_rows: int
    step: ClassVar[str] = "dataset_split"

    def fields(self) -> dict[str, Any]:
        return {
            "rows": self.rows,
            "details": (
                f"train={self.train_rows} "
                f"validation={self.validation_rows} "
                f"test={self.test_rows}"
            ),
        }


@dataclass(frozen=True)
class ModelTrained(ReportEventData):
    partition: str
    rows: int
    model_name: str
    step: ClassVar[str] = "model_trained"

    def fields(self) -> dict[str, Any]:
        return {
            "partition": self.partition,
            "rows": self.rows,
            "model_name": self.model_name,
        }


@dataclass(frozen=True)
class ModelEvaluated(ReportEventData):
    partition: str
    rows: int
    model_name: str
    metrics: Metrics
    step: ClassVar[str] = "model_evaluated"

    def fields(self) -> dict[str, Any]:
        return {
            "partition": self.partition,
            "rows": self.rows,
            "model_name": self.model_name,
            "metrics": self.metrics,
        }


@dataclass(frozen=True)
class ModelSaved(ReportEventData):
    model_path: Path
    step: ClassVar[str] = "model_saved"

    def fields(self) -> dict[str, Any]:
        return {"model_path": self.model_path, "details": str(self.model_path)}


@dataclass(frozen=True)
class ExperimentCompleted(ReportEventData):
    report_path: Path
    step: ClassVar[str] = "experiment_completed"

    def fields(self) -> dict[str, Any]:
        return {"details": str(self.report_path)}


@dataclass(frozen=True)
class DatasetReady(ReportEventData):
    dataset_path: Path
    step: ClassVar[str] = "dataset_ready"

    def fields(self) -> dict[str, Any]:
        return {"details": str(self.dataset_path)}


@dataclass(frozen=True)
class ModelLoaded(ReportEventData):
    model_path: Path
    step: ClassVar[str] = "model_loaded"

    def fields(self) -> dict[str, Any]:
        return {"model_path": self.model_path}


@dataclass(frozen=True)
class DatasetLoaded(ReportEventData):
    rows: int
    dataset_path: Path
    step: ClassVar[str] = "dataset_loaded"

    def fields(self) -> dict[str, Any]:
        return {"rows": self.rows, "details": str(self.dataset_path)}


@dataclass(frozen=True)
class PredictionsGenerated(ReportEventData):
    rows: int
    feature_columns: int
    step: ClassVar[str] = "predictions_generated"

    def fields(self) -> dict[str, Any]:
        return {"rows": self.rows, "details": f"columns={self.feature_columns}"}


@dataclass(frozen=True)
class PredictionCompleted(ReportEventData):
    report_path: Path
    step: ClassVar[str] = "prediction_completed"

    def fields(self) -> dict[str, Any]:
        return {"details": str(self.report_path)}


@dataclass(frozen=True)
class RunCompleted(ReportEventData):
    report_path: Path
    step: ClassVar[str] = "run_completed"

    def fields(self) -> dict[str, Any]:
        return {"details": str(self.report_path)}
