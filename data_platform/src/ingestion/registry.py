from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ingestion.audit_database_ingestor import AuditDatabaseIngestor
from ingestion.audit_datalake_ingestor import AuditDataLakeIngestor
from ingestion.audit_datawarehouse_ingestor import AuditDataWarehouseIngestor
from ingestion.audit_message_queue_ingestor import AuditMessageQueueIngestor
from ingestion.audit_spark_datalake_ingestor import AuditSparkDataLakeIngestor
from ingestion.audit_streaming_channel_ingestor import AuditStreamingChannelIngestor
from ingestion.house_database_ingestor import HouseDatabaseIngestor
from ingestion.house_datalake_ingestor import HouseDataLakeIngestor
from ingestion.house_datawarehouse_ingestor import HouseDataWarehouseIngestor
from ingestion.house_message_queue_ingestor import HouseMessageQueueIngestor
from ingestion.house_rest_api_ingestor import HouseRestApiIngestor
from ingestion.house_spark_datalake_ingestor import HouseSparkDataLakeIngestor
from ingestion.house_streaming_channel_ingestor import HouseStreamingChannelIngestor
from ingestion.sale_database_ingestor import SaleDatabaseIngestor
from ingestion.sale_datalake_ingestor import SaleDataLakeIngestor
from ingestion.sale_datawarehouse_ingestor import SaleDataWarehouseIngestor
from ingestion.sale_message_queue_ingestor import SaleMessageQueueIngestor
from ingestion.sale_rest_api_ingestor import SaleRestApiIngestor
from ingestion.sale_spark_datalake_ingestor import SaleSparkDataLakeIngestor
from ingestion.sale_streaming_channel_ingestor import SaleStreamingChannelIngestor


IngestorFactory = Callable[..., Any]


registry: dict[str, IngestorFactory] = {
    "sale.database": lambda *, table_name: SaleDatabaseIngestor(table_name=table_name),
    "house.database": lambda *, table_name: HouseDatabaseIngestor(table_name=table_name),
    "audit.database": lambda *, table_name: AuditDatabaseIngestor(table_name=table_name),
    "sale.datawarehouse": lambda *, full_table_name: SaleDataWarehouseIngestor(full_table_name=full_table_name),
    "house.datawarehouse": lambda *, full_table_name: HouseDataWarehouseIngestor(full_table_name=full_table_name),
    "audit.datawarehouse": lambda *, full_table_name: AuditDataWarehouseIngestor(full_table_name=full_table_name),
    "sale.datalake": lambda *, bucket_name, relative_path: SaleDataLakeIngestor(bucket_name=bucket_name, relative_path=relative_path),
    "house.datalake": lambda *, bucket_name, relative_path: HouseDataLakeIngestor(bucket_name=bucket_name, relative_path=relative_path),
    "audit.datalake": lambda *, bucket_name, relative_path: AuditDataLakeIngestor(bucket_name=bucket_name, relative_path=relative_path),
    "sale_spark_datalake": lambda *, relative_path, spark: SaleSparkDataLakeIngestor(relative_path=relative_path, spark=spark),
    "house_spark_datalake": lambda *, relative_path, spark: HouseSparkDataLakeIngestor(relative_path=relative_path, spark=spark),
    "audit_spark_datalake": lambda *, relative_path, spark: AuditSparkDataLakeIngestor(relative_path=relative_path, spark=spark),
    "sale.rest.api": lambda *, url: SaleRestApiIngestor(url=url),
    "house.rest.api": lambda *, url: HouseRestApiIngestor(url=url),
    "sale.kafka.listener": lambda *, spark: SaleStreamingChannelIngestor(spark=spark),
    "house.kafka.listener": lambda *, spark: HouseStreamingChannelIngestor(spark=spark),
    "audit.kafka.listener": lambda *, spark: AuditStreamingChannelIngestor(spark=spark),
    "sale.message.queue": lambda *, endpoint: SaleMessageQueueIngestor(endpoint=endpoint),
    "house.message.queue": lambda *, endpoint: HouseMessageQueueIngestor(endpoint=endpoint),
    "audit.message.queue": lambda *, endpoint: AuditMessageQueueIngestor(endpoint=endpoint),
}


def get_ingestor(name: str, **kwargs: Any) -> Any:
    return registry[name](**kwargs)
