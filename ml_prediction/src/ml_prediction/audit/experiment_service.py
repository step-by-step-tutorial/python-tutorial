from pathlib import Path
from typing import cast

from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.audit.data.training_audit_data import TrainingAuditData
from ml_prediction.audit.data.experiment_data import ExperimentData
from ml_prediction.audit.data_service import DataService
from ml_prediction.utils.csv_utils import read_csv, write_csv
from ml_prediction.utils.data_validator_utils import is_none


class ExperimentService(DataService):
    def read(self, path: Path) -> list[ExperimentData]:
        return read_csv(path, ExperimentData.from_row)

    def write(self, data: TrainingAuditData, path: Path) -> None:
        experiment = data.experiment
        if is_none(experiment):
            return
        write_csv(path, [cast(ExperimentData, experiment)])
