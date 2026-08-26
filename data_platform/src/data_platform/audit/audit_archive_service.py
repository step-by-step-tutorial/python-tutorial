import json
import logging
from datetime import datetime
from typing import Any

from data_platform.audit.abstract_audit_service import AbstractAuditService
from data_platform.audit.audit_event import AuditEvent
from data_platform.model.endpoints import AuditEndpoint
from data_platform.registry.connection_registry import connection_registry
from data_platform.util.path_utils import (
    generate_audit_event_key,
    generate_audit_manifest_key,
    generate_full_path,
)

logger = logging.getLogger(__name__)


class AuditArchiveService(AbstractAuditService):

    def __init__(self, audit_endpoint: AuditEndpoint) -> None:
        self._client = connection_registry.get_item(audit_endpoint.datalake_connection_name)
        self._bucket_name = audit_endpoint.bucket_name

    def save(self, event: AuditEvent) -> None:
        self._ensure_bucket_exists()
        object_key = generate_audit_event_key(
            event.event_time, event.pipeline_name, event.pipeline_id, event.event_id
        )
        content = event.model_dump_json(indent=2).encode("utf-8")
        self._client.put_object(
            Bucket=self._bucket_name,
            Key=object_key,
            Body=content,
            ContentLength=len(content),
            ContentType="application/json",
            Metadata={
                "pipeline-name": event.pipeline_name,
                "pipeline-run-id": event.pipeline_id,
                "event-type": event.event_type.value,
                "event-id": str(event.event_id),
            },
        )
        logger.info(
            "Audit event archived: event_id=%s type=%s bucket=%s key=%s bytes=%s",
            event.event_id,
            event.event_type.value,
            self._bucket_name,
            object_key,
            len(content),
        )

    def write_manifest(
            self,
            pipeline_name: str,
            pipeline_id: str,
            manifest: dict[str, Any],
            event_time: datetime
    ) -> str:
        object_key = generate_audit_manifest_key(event_time, pipeline_name, pipeline_id)
        content = json.dumps(manifest, indent=2, default=str).encode("utf-8")
        self._ensure_bucket_exists()
        self._client.put_object(
            Bucket=self._bucket_name,
            Key=object_key,
            Body=content,
            ContentLength=len(content),
            ContentType="application/json",
        )
        logger.info(
            "Audit manifest archived: pipeline=%s pipeline_id=%s bucket=%s key=%s bytes=%s",
            pipeline_name,
            pipeline_id,
            self._bucket_name,
            object_key,
            len(content),
        )
        return generate_full_path(bucket_name=self._bucket_name, relative_path=object_key)

    def _ensure_bucket_exists(self) -> None:
        buckets = self._client.list_buckets()
        bucket_names = {bucket["Name"] for bucket in buckets.get("Buckets", [])}
        if self._bucket_name not in bucket_names:
            self._client.create_bucket(Bucket=self._bucket_name)
            logger.info("Created audit archive bucket: bucket=%s", self._bucket_name)
