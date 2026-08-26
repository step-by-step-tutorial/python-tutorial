from enum import StrEnum


class Key(StrEnum):
    DATA_SIMULATOR_API = "data_simulator.api"
    PLATFORM_DATABASE = "data-platform.database"
    HOUSE_DATABASE = "house.database"
    ONLINE_SHOPPING_DATABASE = "online_shopping.database"
    AUDIT_DATABASE = "audit.database"

    PLATFORM_DATA_LAKE = "data-platform.datalake"
    PLATFORM_BACKUP_DATA_LAKE = "data-platform.backup.datalake"
    HOUSE_DATA_LAKE = "house.datalake"
    HOUSE_BACKUP_DATA_LAKE = "house.backup.datalake"
    AUDIT_DATA_LAKE = "audit.datalake"

    PLATFORM_WAREHOUSE = "data-platform.warehouse"
    HOUSE_WAREHOUSE = "house.warehouse"
    ONLINE_SHOPPING_WAREHOUSE = "online_shopping.warehouse"
    AUDIT_WAREHOUSE = "audit.warehouse"

    HOUSE_CSV_FILE = "house.file.csv"
    HOUSE_REST_API = "house.rest.api"
    ONLINE_SHOPPING_REST_API = "online_shopping.rest.api"
    ONLINE_SHOPPING_KAFKA_CONSUMER = "online_shopping.kafka.listener"
    ONLINE_SHOPPING_DATA_LAKE = "online_shopping.datalake"
    ONLINE_SHOPPING_BACKUP_DATA_LAKE = "online_shopping.backup.datalake"

    HOUSE_KAFKA_CONSUMER = "house.kafka.listener"
    AUDIT_KAFKA_PRODUCER = "audit.kafka.producer"
    AUDIT_KAFKA_CONSUMER = "audit.kafka.listener"
    HOUSE_KAFKA_PRODUCER = "house.kafka.producer"
