from config.app import settings as app_settings
from config.audit import settings as audit_settings
from config.datalake import settings as datalake_settings
from config.datawarehouse import settings as datawarehouse_settings
from config.messaging import settings as messaging_settings
from dataset.definition import (
    Audit,
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
    audit=Audit(
        topic=audit_settings.streaming_topic,
        archive_enabled=audit_settings.archive_enabled,
    ),
    sources={
        "file": FileEndpoint(
            name="file",
            file_name="sale.csv",
            file_path=str(app_settings.root / app_settings.resources_dir / "sale.csv"),
        ),
        "messaging": MessagingEndpoint(
            name="messaging",
            topic=messaging_settings.topic,
        ),
    },
    destinations={
        "datalake": DataLakeEndpoint(name="datalake", bucket_name=datalake_settings.bucket_name),
        "database": DatabaseEndpoint(
            name="database",
            table_name="sale.sale_stage",
            before_setup_sql_files=("database/sale/truncate_stage.sql",),
            after_setup_sql_files=(
                "database/sale/upsert_customer.sql",
                "database/sale/upsert_product.sql",
                "database/sale/upsert_order.sql",
                "database/sale/upsert_order_item.sql",
            ),
        ),
        "datawarehouse": DataWarehouseEndpoint(
            name="datawarehouse",
            table_name="sale_table",
            full_table_name=f"{datawarehouse_settings.database_name}.sale_table",
            before_setup_sql_files={
                "truncate": "datawarehouse/sale/truncate_datawarehouse.sql"
            },
            after_setup_sql_files={
                "revenue_by_category": "datawarehouse/sale/select_revenue_by_category.sql",
                "revenue_by_country": "datawarehouse/sale/select_revenue_by_country.sql",
            },
        ),
    },
    processor_factories={
        "inmemory": InmemorySaleProcessor,
        "spark": SparkSaleProcessor,
    },
)
