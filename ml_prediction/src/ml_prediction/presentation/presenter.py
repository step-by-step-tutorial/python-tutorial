from abc import ABC, abstractmethod
from typing import Any

from ml_prediction.audit.data.training_audit_data import TrainingAuditData


class Presenter(ABC):
    @abstractmethod
    def present(self, output: TrainingAuditData) -> Any:
        raise NotImplementedError
