from abc import ABC, abstractmethod
from typing import Any

from ml_prediction.audit.data.experiment_audit_data import ExperimentAuditData


class Presenter(ABC):
    @abstractmethod
    def present(self, output: ExperimentAuditData) -> Any:
        raise NotImplementedError
