from enum import StrEnum


class Key(StrEnum):
    TEST_DATA_API = "test_data.api"
    PLATFORM_DATABASE = "data-platform.database"
    SALE_DATABASE = "sale.database"
    HOUSE_DATABASE = "house.database"
    ONLINE_SHOPPING_DATABASE = "online_shopping.database"
    AUDIT_DATABASE = "audit.database"

    PLATFORM_DATA_LAKE = "data-platform.datalake"
    SALE_DATA_LAKE = "sale.datalake"
    HOUSE_DATA_LAKE = "house.datalake"
    AUDIT_DATA_LAKE = "audit.datalake"

    PLATFORM_DATA_WAREHOUSE = "data-platform.datawarehouse"
    SALE_DATA_WAREHOUSE = "sale.datawarehouse"
    HOUSE_DATA_WAREHOUSE = "house.datawarehouse"
    ONLINE_SHOPPING_DATA_WAREHOUSE = "online_shopping.datawarehouse"
    AUDIT_DATA_WAREHOUSE = "audit.datawarehouse"

    SALE_CSV_FILE = "sale.file.csv"
    HOUSE_CSV_FILE = "house.file.csv"

    SALE_REST_API = "sale.rest"

    ONLINE_SHOPPING_REST_API = "online_shopping.rest.api"
    ONLINE_SHOPPING_DATA_LAKE = "online_shopping.datalake"

    SALE_KAFKA_CONSUMER = "sale.kafka.listener"
    HOUSE_KAFKA_CONSUMER = "house.kafka.listener"
    AUDIT_KAFKA_PRODUCER = "audit.kafka.producer"
    AUDIT_KAFKA_CONSUMER = "audit.kafka.listener"
    SALE_KAFKA_PRODUCER = "sale.kafka.producer"
    HOUSE_KAFKA_PRODUCER = "house.kafka.producer"

