from data_platform.config.main_settings import settings as main_settings
from data_platform.dataset.endpoint_registry import endpoint_registry
from data_platform.keys import Key
from data_platform.model import AuditEndpoint

AUDIT_ENDPOINT = AuditEndpoint(
    database_connection_name=Key.AUDIT_DATABASE,
    messaging_connection_name=Key.AUDIT_KAFKA_PRODUCER,
    datalake_connection_name=Key.AUDIT_DATALAKE,
    schema="audit",
    create_sql_files={"create": "database/audit/create_tables.sql"},
    channel_name=main_settings.messaging[Key.AUDIT_KAFKA_PRODUCER].audit_channel_name,
    bucket_name=main_settings.data_lake[Key.AUDIT_DATALAKE].audit_bucket_name,
    write_sql_files={"write": "database/audit/insert_event.sql"},
)

endpoint_registry.register(AUDIT_ENDPOINT)
