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
    Event,
    FileEndpoint,
    MessagingEndpoint,
)
from dataset.sale.columns import sale_columns as columns
from dataset.sale.spark_schema import build_schema
from model.sale_event import SaleEvent


def _schema():
    return build_schema()


def _inmemory_processor():
    from processor.inmemory.sale_processor import InmemorySaleProcessor

    return InmemorySaleProcessor()


def _spark_processor():
    from processor.spark.sale_processor import SparkSaleProcessor

    return SparkSaleProcessor()


SALE_DATASET = Dataset(
    name="Sale",
    dataframe=Dataframe(
        schema_factory=_schema,
        required_columns=frozenset(
            {
                columns.order_id,
                columns.customer_name,
                columns.product_name,
                columns.category,
                columns.quantity,
                columns.unit_price,
                columns.order_date,
                columns.country,
            }
        ),
    ),
    event=Event(
        key_column=columns.order_id,
        converter=lambda row: SaleEvent.from_dict(row).to_dict(),
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
            before_load_sql_files=("database/sale/truncate_stage.sql",),
            after_load_sql_files=(
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
            preparing_sql_files={
                "truncate": "datawarehouse/sale/truncate_datawarehouse.sql"
            },
            analysis_sql_files={
                "revenue_by_category": "datawarehouse/sale/select_revenue_by_category.sql",
                "revenue_by_country": "datawarehouse/sale/select_revenue_by_country.sql",
            },
        ),
    },
    processor_factories={
        "inmemory": _inmemory_processor,
        "spark": _spark_processor,
    },
)
