import json
from datetime import datetime
from typing import Any

from factory import datalake_connection_factory
from model.audit_event import AuditEvent
from util.datalake_utils import generate_full_path


def save_event(event: AuditEvent, bucket_name: str) -> str:
    object_key = (
        f"events/event_date={event.event_time.date().isoformat()}"
        f"/pipeline_name={event.pipeline_name}"
        f"/pipeline_id={event.pipeline_id}/{event.event_id}.json"
    )
    content = event.model_dump_json(indent=2).encode("utf-8")
    with datalake_connection_factory.create_connection() as client:
        client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=content,
            ContentLength=len(content),
            ContentType="application/json",
            Metadata={
                "pipeline-name": event.pipeline_name,
                "pipeline-run-id": event.pipeline_id,
                "event-type": event.event_type.value,
                "event-id": str(event.event_id)
            }
        )
    return generate_full_path(bucket_name=bucket_name, relative_path=object_key)


def save_manifest(
        pipeline_name: str,
        pipeline_id: str,
        manifest: dict[str, Any],
        event_time: datetime,
        bucket_name: str
) -> str:
    object_key = (
        f"manifests/event_date={event_time.date().isoformat()}"
        f"/pipeline_name={pipeline_name}"
        f"/pipeline_id={pipeline_id}"
        f"/pipeline_manifest.json"
    )
    content = json.dumps(manifest, indent=2, default=str).encode("utf-8")
    with datalake_connection_factory.create_connection() as client:
        client.put_object(
            Bucket=bucket_name,
            Key=object_key, Body=content,
            ContentLength=len(content),
            ContentType="application/json"
        )
    return generate_full_path(bucket_name=bucket_name, relative_path=object_key)
