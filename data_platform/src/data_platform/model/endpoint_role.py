from enum import StrEnum


class EndpointRole(StrEnum):
    FILE_CSV = "file.csv"
    DATABASE = "database"
    DATA_LAKE = "datalake"
    DATA_WAREHOUSE = "datawarehouse"
    KAFKA_LISTENER = "kafka.listener"
    KAFKA_PRODUCER = "kafka.producer"
