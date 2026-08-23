
from typing import Any

from connector.spark_session_factory import create_session
from dataset.sale.config import SALE_DATASET
from keys import Key
from ingestion.csv_file_ingestor import CsvFileIngestor
from ingestion.database_ingestor import DatabaseIngestor
from ingestion.datalake_ingestor import DataLakeIngestor
from ingestion.datawarehouse_ingestor import DataWarehouseIngestor
from ingestion.kafka_ingestor import KafkaIngestor
from ingestion.rest_api_ingestor import RestApiIngestor
from ingestion.spark_csv_file_ingestor import SparkCsvFileIngestor
from ingestion.spark_datalake_ingestor import SparkDataLakeIngestor
from ingestion.spark_kafka_ingestor import SparkKafkaIngestor

registry: dict[str, Any] = {
    Key.SALE_FILE_CSV: CsvFileIngestor(SALE_DATASET.endpoints[Key.SALE_FILE_CSV]),
    Key.SALE_DATABASE: DatabaseIngestor(SALE_DATASET.endpoints[Key.SALE_DATABASE]),
    Key.SALE_DATAWAREHOUSE: DataWarehouseIngestor(SALE_DATASET.endpoints[Key.SALE_DATAWAREHOUSE]),
    Key.SALE_DATALAKE: DataLakeIngestor(SALE_DATASET.endpoints[Key.SALE_DATALAKE]),
    Key.SALE_KAFKA_LISTENER: KafkaIngestor(SALE_DATASET.endpoints[Key.SALE_KAFKA_LISTENER]),
    Key.SALE_REST: RestApiIngestor(SALE_DATASET.endpoints[Key.SALE_REST]),
}

SPARK_INGESTORS = {
    Key.SALE_SPARK_CSV,
    Key.SALE_SPARK_DATALAKE,
    Key.SALE_SPARK_KAFKA,
}


def _is_session_active(session: Any) -> bool:
    try:
        spark_context = session.sparkContext
        jsc = getattr(spark_context, "_jsc", None)
        return jsc is not None and not jsc.sc().isStopped()
    except Exception:
        return False


def get_ingestor(name: str) -> Any:
    if name not in SPARK_INGESTORS:
        return registry[name]

    ingestor = registry.get(name)
    session = getattr(ingestor, "session", None)
    if session is not None and _is_session_active(session):
        return ingestor

    session = create_session()
    if name == Key.SALE_SPARK_CSV:
        ingestor = SparkCsvFileIngestor(session)
    elif name == Key.SALE_SPARK_DATALAKE:
        ingestor = SparkDataLakeIngestor(SALE_DATASET.endpoints[Key.SALE_DATALAKE], session)
    else:
        ingestor = SparkKafkaIngestor(
            SALE_DATASET.endpoints[Key.SALE_KAFKA_LISTENER],
            session,
            SALE_DATASET.dataframe.schema,
        )
    registry[name] = ingestor
    return ingestor
