from ml_prediction.audit.data.experiment_data import ExperimentData
from ml_prediction.audit.experiment_service import ExperimentService
from ml_prediction.config.settings import get_settings


class ExperimentComparisonService:
    def __init__(self, dataset_name: str) -> None:
        self.dataset_name = dataset_name
        settings = get_settings(dataset_name)
        self.repository = ExperimentService()
        self.experiment_path = settings.audit_dir / settings.experiment_filename

    def best_by_validation_mae(self) -> ExperimentData | None:
        experiments = self.repository.read(self.experiment_path)
        return min(
            experiments,
            key=lambda experiment: experiment.validation_metrics.mean_absolute_error,
            default=None,
        )

    def best_by_validation_rmse(self) -> ExperimentData | None:
        experiments = self.repository.read(self.experiment_path)
        return min(
            experiments,
            key=lambda experiment: experiment.validation_metrics.root_mean_squared_error,
            default=None,
        )

    def best_by_validation_r2(self) -> ExperimentData | None:
        experiments = self.repository.read(self.experiment_path)
        return max(
            experiments,
            key=lambda experiment: experiment.validation_metrics.r2_score,
            default=None,
        )

    def best_by_validation_accuracy(self) -> ExperimentData | None:
        experiments = self.repository.read(self.experiment_path)
        return max(
            experiments,
            key=lambda experiment: experiment.validation_metrics.accuracy,
            default=None,
        )

    def best_by_validation_precision(self) -> ExperimentData | None:
        experiments = self.repository.read(self.experiment_path)
        return max(
            experiments,
            key=lambda experiment: experiment.validation_metrics.precision,
            default=None,
        )

    def best_by_validation_recall(self) -> ExperimentData | None:
        experiments = self.repository.read(self.experiment_path)
        return max(
            experiments,
            key=lambda experiment: experiment.validation_metrics.recall,
            default=None,
        )

    def best_by_validation_f1_score(self) -> ExperimentData | None:
        experiments = self.repository.read(self.experiment_path)
        return max(
            experiments,
            key=lambda experiment: experiment.validation_metrics.f1_score,
            default=None,
        )
