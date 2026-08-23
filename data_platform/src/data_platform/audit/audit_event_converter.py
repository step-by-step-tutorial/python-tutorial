import json
from typing import Any

from data_platform.model.audit_event import AuditEvent


def to_persistable_event(event: AuditEvent) -> dict[str, Any]:
    parameters = event.model_dump(mode="json")
    parameters["metadata"] = json.dumps(parameters["metadata"])
    return parameters
