from abc import ABC, abstractmethod

from data_platform.model.audit_event import AuditEvent


class AbstractAuditService(ABC):

    @abstractmethod
    def write(self, event: AuditEvent) -> None:
        raise NotImplementedError
