from abc import ABC, abstractmethod

from data_platform.audit.audit_event import AuditEvent


class AbstractAuditService(ABC):

    @abstractmethod
    def save(self, event: AuditEvent) -> None:
        raise NotImplementedError
