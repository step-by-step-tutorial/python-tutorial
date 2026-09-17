from pathlib import Path

from ml_prediction.audit.data.audit_data import AuditData
from ml_prediction.audit.data.experiment_audit_data import ExperimentAuditData
from ml_prediction.audit.data.experiment_data import ExperimentData
from ml_prediction.audit.data_service import DataService
from ml_prediction.utils.csv_utils import read_csv, write_csv


class ExperimentService(DataService):
    def read(self, path: Path) -> list[ExperimentData]:
        return read_csv(path, ExperimentData.from_row)

    def write(self, data: AuditData, path: Path) -> AuditData | None:
        if not isinstance(data, ExperimentAuditData):
            return None
        write_csv(path, [data.experiment])
        return data
