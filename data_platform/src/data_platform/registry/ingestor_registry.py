
from typing import Any

from data_platform.ingestion.ingestor_loaders import (
    load_house_data_lake,
    load_house_data_warehouse,
    load_house_database,
    load_house_file_csv,
    load_house_kafka_listener,
    load_house_kafka_producer,
    load_sale_data_lake,
    load_sale_data_warehouse,
    load_sale_database,
    load_sale_file_csv,
    load_sale_kafka_listener,
    load_sale_kafka_producer,
    load_sale_rest_api,
    load_sale_spark_csv,
    load_sale_spark_data_lake,
    load_sale_spark_kafka,
)
from data_platform.keys import Key
from data_platform.registry.base_registry import Registry


class IngestorRegistry(Registry[Any]):
    def __init__(self) -> None:
        super().__init__("ingestor")


ingestor_registry = IngestorRegistry()

ingestor_registry.register_lazy_item(Key.SALE_FILE_CSV, load_sale_file_csv)
ingestor_registry.register_lazy_item(Key.SALE_REST, load_sale_rest_api)
ingestor_registry.register_lazy_item(Key.SALE_KAFKA_LISTENER, load_sale_kafka_listener)
ingestor_registry.register_lazy_item(Key.SALE_KAFKA_PRODUCER, load_sale_kafka_producer)
ingestor_registry.register_lazy_item(Key.SALE_DATALAKE, load_sale_data_lake)
ingestor_registry.register_lazy_item(Key.SALE_DATABASE, load_sale_database)
ingestor_registry.register_lazy_item(Key.SALE_DATAWAREHOUSE, load_sale_data_warehouse)
ingestor_registry.register_lazy_item(Key.HOUSE_FILE_CSV, load_house_file_csv)
ingestor_registry.register_lazy_item(Key.HOUSE_KAFKA_LISTENER, load_house_kafka_listener)
ingestor_registry.register_lazy_item(Key.HOUSE_KAFKA_PRODUCER, load_house_kafka_producer)
ingestor_registry.register_lazy_item(Key.HOUSE_DATALAKE, load_house_data_lake)
ingestor_registry.register_lazy_item(Key.HOUSE_DATABASE, load_house_database)
ingestor_registry.register_lazy_item(Key.HOUSE_DATAWAREHOUSE, load_house_data_warehouse)
ingestor_registry.register_lazy_item(Key.SALE_SPARK_CSV, load_sale_spark_csv, cache=False)
ingestor_registry.register_lazy_item(Key.SALE_SPARK_DATALAKE, load_sale_spark_data_lake, cache=False)
ingestor_registry.register_lazy_item(Key.SALE_SPARK_KAFKA, load_sale_spark_kafka, cache=False)
