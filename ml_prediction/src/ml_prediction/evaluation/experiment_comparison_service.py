from ml_prediction.model.experiment_result import ExperimentResult
from ml_prediction.reporting.experiment_repository import ExperimentRepository


class ExperimentComparisonService:
    def __init__(self, experiment_repository: ExperimentRepository, dataset_name: str) -> None:
        self.repository = experiment_repository
        self.dataset_name = dataset_name


    def best_by_validation_mae(self) -> ExperimentResult | None:
        experiments = self.repository.read_all(self.dataset_name)
        return min(
            experiments,
            key=lambda experiment: experiment.validation_metrics.mean_absolute_error,
            default=None,
        )

    def best_by_validation_rmse(self) -> ExperimentResult | None:
        experiments = self.repository.read_all(self.dataset_name)
        return min(
            experiments,
            key=lambda experiment: experiment.validation_metrics.root_mean_squared_error,
            default=None,
        )

    def best_by_validation_r2(self) -> ExperimentResult | None:
        experiments = self.repository.read_all(self.dataset_name)
        return max(
            experiments,
            key=lambda experiment: experiment.validation_metrics.r2_score,
            default=None,
        )
