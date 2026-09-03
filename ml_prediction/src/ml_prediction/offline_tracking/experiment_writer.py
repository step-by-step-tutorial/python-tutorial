from ml_prediction.config.settings import get_settings
from ml_prediction.offline_tracking.models import Experiment
from ml_prediction.utils.csv_utils import write_csv


class ExperimentWriter:
    def __init__(self, dataset_name: str) -> None:
        settings = get_settings(dataset_name)
        self.path = settings.report_dir / settings.experiment_filename

    def save(self, experiment: Experiment) -> None:
        write_csv(self.path, [experiment], Experiment.fieldnames, Experiment.to_row)
