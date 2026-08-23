from enum import StrEnum


class Key(StrEnum):
    DATA_PLATFORM_DATABASE = "data-platform.database"
    SALE_DATABASE = "sale.database"
    HOUSE_DATABASE = "house.database"
    AUDIT_DATABASE = "audit.database"

    DATA_PLATFORM_DATALAKE = "data-platform.datalake"
    SALE_DATALAKE = "sale.datalake"
    HOUSE_DATALAKE = "house.datalake"
    AUDIT_DATALAKE = "audit.datalake"

    DATA_PLATFORM_DATAWAREHOUSE = "data-platform.datawarehouse"
    SALE_DATAWAREHOUSE = "sale.datawarehouse"
    HOUSE_DATAWAREHOUSE = "house.datawarehouse"
    AUDIT_DATAWAREHOUSE = "audit.datawarehouse"

    SALE_FILE_CSV = "sale.file.csv"
    HOUSE_FILE_CSV = "house.file.csv"

    SALE_REST = "sale.rest"

    SALE_KAFKA_LISTENER = "sale.kafka.listener"
    HOUSE_KAFKA_LISTENER = "house.kafka.listener"
    AUDIT_KAFKA_PRODUCER = "audit.kafka.producer"
    AUDIT_KAFKA_LISTENER = "audit.kafka.listener"
    SALE_KAFKA_PRODUCER = "sale.kafka.producer"
    HOUSE_KAFKA_PRODUCER = "house.kafka.producer"

    SALE_SPARK_CSV = "sale.spark.csv"
    SALE_SPARK_DATALAKE = "sale.spark.datalake"
    SALE_SPARK_KAFKA = "sale.spark.kafka"
    HOUSE_SPARK_CSV = "house.spark.csv"
    HOUSE_SPARK_KAFKA = "house.spark.kafka"
