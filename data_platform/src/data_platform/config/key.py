from enum import StrEnum


class Key(StrEnum):
    PLATFORM_DATA_LAKE = "data-platform.datalake"

    AUDIT = "audit"
    AUDIT_DATABASE = "audit.database"
    AUDIT_DATA_LAKE = "audit.datalake"
    AUDIT_WAREHOUSE = "audit.warehouse"
    AUDIT_MESSAGING = "audit.messaging"
    AUDIT_KAFKA_PRODUCER = "audit.kafka.producer"
    AUDIT_KAFKA_CONSUMER = "audit.kafka.listener"

    HOUSE_CSV_FILE = "house.file.csv"
    HOUSE_REST_API = "house.rest.api"
    HOUSE_DATABASE = "house.database"
    HOUSE_DATA_LAKE = "house.datalake"
    HOUSE_BACKUP_DATA_LAKE = "house.backup.datalake"
    HOUSE_WAREHOUSE = "house.warehouse"
    HOUSE_MESSAGING = "house.messaging"
    HOUSE_KAFKA_PRODUCER = "house.kafka.producer"
    HOUSE_KAFKA_CONSUMER = "house.kafka.listener"

    ONLINE_SHOPPING_REST_API = "online_shopping.rest.api"
    ONLINE_SHOPPING_DATABASE = "online_shopping.database"
    ONLINE_SHOPPING_DATA_LAKE = "online_shopping.datalake"
    ONLINE_SHOPPING_BACKUP_DATA_LAKE = "online_shopping.backup.datalake"
    ONLINE_SHOPPING_WAREHOUSE = "online_shopping.warehouse"
    ONLINE_SHOPPING_MESSAGING = "online_shopping.messaging"
    ONLINE_SHOPPING_KAFKA_CONSUMER = "online_shopping.kafka.listener"
