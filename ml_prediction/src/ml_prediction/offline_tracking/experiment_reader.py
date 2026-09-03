from ml_prediction.config.settings import get_settings
from ml_prediction.offline_tracking.models import Experiment
from ml_prediction.offline_tracking.experiment_writer import ExperimentWriter
from ml_prediction.utils.csv_utils import read_csv


class ExperimentReader:
    def __init__(self, dataset_name: str) -> None:
        settings = get_settings(dataset_name)
        self.path = settings.report_dir / settings.experiment_filename

    def read_all(self) -> list[Experiment]:
        return read_csv(self.path, Experiment.from_row)

    def save(self, experiment: Experiment) -> None:
        writer = ExperimentWriter.__new__(ExperimentWriter)
        writer.path = self.path
        writer.save(experiment)
