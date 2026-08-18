from config.app import settings as app_settings
from config.audit import settings as audit_settings
from config.datalake import settings as datalake_settings
from config.datawarehouse import settings as datawarehouse_settings
from config.messaging import settings as messaging_settings
from config.streaming import settings as streaming_settings
from dataset.definition import (
    AuditEndpoint,
    DataLakeEndpoint,
    DataWarehouseEndpoint,
    Dataframe,
    DatabaseEndpoint,
    Dataset,
    FileEndpoint,
    MessagingEndpoint,
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
        database_connection_name="audit.database",
        messaging_connection_name="audit.kafka.producer",
        datalake_connection_name="audit.datalake",
        create_sql_files={"create": "database/audit/create_tables.sql"},
        channel_name=audit_settings.channel_name,
        bucket_name=audit_settings.archive_bucket_name,
        write_sql_files={"write": "database/audit/insert_event.sql"},
    ),
    endpoints={
        "sale.file.csv": FileEndpoint(
            name="file",
            file_name="sale.csv",
            file_path=str(app_settings.root / app_settings.resources_dir / "sale.csv"),
        ),
        "sale.kafka.listener": MessagingEndpoint(
            name="messaging",
            connection_name="sale.kafka.listener",
            channel_name=messaging_settings.channel_name,
            bootstrap_servers=messaging_settings.bootstrap_servers,
            starting_offsets=streaming_settings.starting_offsets,
        ),
        "sale.datalake": DataLakeEndpoint(
            name="datalake",
            connection_name="sale.datalake",
            bucket_name=datalake_settings.bucket_name,
            scheme=datalake_settings.scheme,
        ),
        "sale.database": DatabaseEndpoint(
            name="database",
            connection_name="sale.database",
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
            query_sql_files={},
        ),
        "sale.datawarehouse": DataWarehouseEndpoint(
            name="datawarehouse",
            connection_name="sale.datawarehouse",
            schema=datawarehouse_settings.database_name,
            table_name="sale_table",
            full_table_name=f"{datawarehouse_settings.database_name}.sale_table",
            create_sql_files={
                "create_database": "datawarehouse/sale/create_database.sql",
                "create_table": "datawarehouse/sale/create_table.sql",
            },
            truncate_sql_files={
                "truncate": "datawarehouse/sale/truncate_datawarehouse.sql"
            },
            write_sql_files={},
            query_sql_files={
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
