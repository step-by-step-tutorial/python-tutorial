from ml_prediction.data_model.experiment import Experiment
from ml_prediction.reporting.experiment_service import ExperimentService


class ExperimentComparisonService:
    def __init__(self, dataset_name: str) -> None:
        self.dataset_name = dataset_name
        self.repository = ExperimentService(dataset_name)


    def best_by_validation_mae(self) -> Experiment | None:
        experiments = self.repository.read_all()
        return min(
            experiments,
            key=lambda experiment: experiment.validation_metrics.mean_absolute_error,
            default=None,
        )

    def best_by_validation_rmse(self) -> Experiment | None:
        experiments = self.repository.read_all()
        return min(
            experiments,
            key=lambda experiment: experiment.validation_metrics.root_mean_squared_error,
            default=None,
        )

    def best_by_validation_r2(self) -> Experiment | None:
        experiments = self.repository.read_all()
        return max(
            experiments,
            key=lambda experiment: experiment.validation_metrics.r2_score,
            default=None,
        )
