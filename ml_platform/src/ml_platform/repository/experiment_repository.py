from pathlib import Path

from ml_platform.model.experiment_model import ExperimentModel
from ml_platform.util.csv_utils import append_rows, read_rows


class ExperimentRepository:
    def __init__(self, path: Path) -> None:
        self._path = path

    def append(self, experiment: ExperimentModel) -> None:
        append_rows(self._path, [experiment.to_dict()])

    def find_all(self) -> list[ExperimentModel]:
        return read_rows(self._path, ExperimentModel.from_dict)
