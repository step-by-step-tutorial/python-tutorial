from abc import ABC, abstractmethod

from data_platform.model.audit_event_model import AuditEventModel


class AbstractAuditService(ABC):

    @abstractmethod
    def save(self, event: AuditEventModel) -> None:
        raise NotImplementedError
