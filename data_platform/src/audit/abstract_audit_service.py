from __future__ import annotations

from abc import ABC, abstractmethod

from model.audit_event import AuditEvent


class AbstractAuditService(ABC):

    @abstractmethod
    def write(self, event: AuditEvent) -> None:
        raise NotImplementedError
