import json
from typing import Any

from model.audit_event import AuditEvent


def to_audit_event_model(event: AuditEvent, streaming_topic: str) -> dict[str, Any]:
    parameters = event.model_dump(mode="json")
    parameters["metadata"] = json.dumps(parameters["metadata"])
    parameters["streaming_topic"] = streaming_topic
    return parameters
