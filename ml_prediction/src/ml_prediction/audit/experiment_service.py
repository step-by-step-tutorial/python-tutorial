from pathlib import Path
from typing import cast

from ml_prediction.audit.data.experiment_dto import ExperimentDto
from ml_prediction.audit.data.training_audit_dto import TrainingAuditDto
from ml_prediction.audit.data_service import DataService
from ml_prediction.utils.csv_utils import read_csv, write_csv
from ml_prediction.utils.data_validator_utils import is_none


class ExperimentService(DataService):
    def read(self, path: Path) -> list[ExperimentDto]:
        return read_csv(path, ExperimentDto.from_dict)

    def write(self, dto: TrainingAuditDto, path: Path) -> None:
        experiment = dto.experiment
        if is_none(experiment):
            return
        write_csv(path, [cast(ExperimentDto, experiment)])
