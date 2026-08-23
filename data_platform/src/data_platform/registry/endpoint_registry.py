from data_platform.config.main_settings import settings as main_settings
from data_platform.config.keys import Key
from data_platform.model import AuditEndpoint, Endpoint
from data_platform.registry.base_registry import Registry


class EndpointRegistry(Registry[Endpoint]):
    def __init__(self) -> None:
        super().__init__("endpoint")


endpoint_registry = EndpointRegistry()

audit_endpoint = AuditEndpoint(
    database_connection_name=Key.AUDIT_DATABASE,
    messaging_connection_name=Key.AUDIT_KAFKA_PRODUCER,
    datalake_connection_name=Key.AUDIT_DATA_LAKE,
    schema="audit",
    create_sql_files={"create": "database/audit/create_tables.sql"},
    channel_name=main_settings.messaging[Key.AUDIT_KAFKA_PRODUCER].audit_channel_name,
    bucket_name=main_settings.data_lake[Key.AUDIT_DATA_LAKE].audit_bucket_name,
    write_sql_files={"write": "database/audit/insert_event.sql"},
)

endpoint_registry.register(audit_endpoint.name, audit_endpoint)
