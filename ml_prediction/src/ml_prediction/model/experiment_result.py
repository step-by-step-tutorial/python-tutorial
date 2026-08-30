from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from ml_prediction.evaluation.model_evaluator import RegressionMetrics


@dataclass(frozen=True)
class ExperimentResult:
    experiment_id: str
    timestamp: datetime
    dataset_name: str
    model_type: str
    model_parameters: dict[str, Any]
    baseline_validation_metrics: RegressionMetrics
    validation_metrics: RegressionMetrics
    test_metrics: RegressionMetrics
    model_path: Path
    report_path: Path | None
