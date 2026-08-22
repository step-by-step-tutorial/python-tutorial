from config.settings import settings as main_settings
from keys import Key
from dataset.definition import (
    AuditEndpoint,
    DataLakeEndpoint,
    DataWarehouseEndpoint,
    Dataframe,
    DatabaseEndpoint,
    Dataset,
    FileEndpoint,
    MessagingEndpoint,
    RestApiEndpoint,
)
from dataset.sale.attribute import SALE_ATTRIBUTE
from dataset.sale.spark_schema import build_schema
from processor.inmemory.sale_processor import InmemorySaleProcessor
from processor.spark.sale_processor import SparkSaleProcessor

SALE_DATASET = Dataset(
    name="Sale",
    dataframe=Dataframe(
        schema=build_schema(),
        required_columns=frozenset(
            {
                SALE_ATTRIBUTE.order_id,
                SALE_ATTRIBUTE.customer_name,
                SALE_ATTRIBUTE.product_name,
                SALE_ATTRIBUTE.category,
                SALE_ATTRIBUTE.quantity,
                SALE_ATTRIBUTE.unit_price,
                SALE_ATTRIBUTE.order_date,
                SALE_ATTRIBUTE.country,
            }
        ),
    ),
    audit=AuditEndpoint(
        database_connection_name=Key.AUDIT_DATABASE,
        messaging_connection_name=Key.AUDIT_KAFKA_PRODUCER,
        datalake_connection_name=Key.AUDIT_DATALAKE,
        schema="audit",
        create_sql_files={"create": "database/audit/create_tables.sql"},
        channel_name=main_settings.messaging[Key.AUDIT_KAFKA_PRODUCER].audit_channel_name,
        bucket_name=main_settings.datalake[Key.AUDIT_DATALAKE].audit_bucket_name,
        write_sql_files={"write": "database/audit/insert_event.sql"},
    ),
    endpoints={
        Key.SALE_FILE_CSV: FileEndpoint(
            name=Key.SALE_FILE_CSV,
            file_name="sale.csv",
            file_path=str(main_settings.app.root / main_settings.app.resources_dir / "sale.csv"),
        ),
        Key.SALE_REST: RestApiEndpoint(
            name=Key.SALE_REST,
            url=main_settings.test_data.download_url,
        ),
        Key.SALE_KAFKA_LISTENER: MessagingEndpoint(
            name=Key.SALE_KAFKA_LISTENER,
            connection_name=Key.SALE_KAFKA_LISTENER,
            channel_name=main_settings.messaging[Key.SALE_KAFKA_LISTENER].channel_name,
            bootstrap_servers=main_settings.messaging[Key.SALE_KAFKA_LISTENER].bootstrap_servers,
            starting_offsets=main_settings.messaging[Key.SALE_KAFKA_LISTENER].starting_offsets,
        ),
        Key.SALE_KAFKA_PRODUCER: MessagingEndpoint(
            name=Key.SALE_KAFKA_PRODUCER,
            connection_name=Key.SALE_KAFKA_PRODUCER,
            channel_name=main_settings.messaging[Key.SALE_KAFKA_PRODUCER].channel_name,
            bootstrap_servers=main_settings.messaging[Key.SALE_KAFKA_PRODUCER].bootstrap_servers,
        ),
        Key.SALE_DATALAKE: DataLakeEndpoint(
            name=Key.SALE_DATALAKE,
            connection_name=Key.SALE_DATALAKE,
            bucket_name=main_settings.datalake[Key.SALE_DATALAKE].bucket_name,
            scheme=main_settings.datalake[Key.SALE_DATALAKE].scheme,
        ),
        Key.SALE_DATABASE: DatabaseEndpoint(
            name=Key.SALE_DATABASE,
            connection_name=Key.SALE_DATABASE,
            schema="sale",
            stage_table_name="sale_stage",
            full_stage_table_name="sale.sale_stage",
            table_names=[
                "sale.sale_stage",
                "sale.customer",
                "sale.product",
                "sale.order",
                "sale.order_item",
            ],
            create_sql_files={"create": "database/sale/create_tables.sql"},
            truncate_sql_files={"truncate": "database/sale/truncate_stage.sql"},
            write_sql_files={
                "customer": "database/sale/upsert_customer.sql",
                "product": "database/sale/upsert_product.sql",
                "order": "database/sale/upsert_order.sql",
                "order_item": "database/sale/upsert_order_item.sql",
            },
            query_sql_files={"select_all": "database/select_all.sql"},
        ),
        Key.SALE_DATAWAREHOUSE: DataWarehouseEndpoint(
            name=Key.SALE_DATAWAREHOUSE,
            connection_name=Key.SALE_DATAWAREHOUSE,
            schema=main_settings.datawarehouse[Key.SALE_DATAWAREHOUSE].database_name,
            table_name="sale_table",
            full_table_name=f"{main_settings.datawarehouse[Key.SALE_DATAWAREHOUSE].database_name}.sale_table",
            create_sql_files={
                "create_database": "datawarehouse/sale/create_database.sql",
                "create_table": "datawarehouse/sale/create_table.sql",
            },
            truncate_sql_files={
                "truncate": "datawarehouse/sale/truncate_datawarehouse.sql"
            },
            write_sql_files={},
            query_sql_files={
                "select_all": "datawarehouse/select_all.sql",
                "revenue_by_category": "datawarehouse/sale/select_revenue_by_category.sql",
                "revenue_by_country": "datawarehouse/sale/select_revenue_by_country.sql",
            },
        ),
    },
    processors={
        "inmemory": InmemorySaleProcessor(),
        "spark": SparkSaleProcessor(),
    },
)
