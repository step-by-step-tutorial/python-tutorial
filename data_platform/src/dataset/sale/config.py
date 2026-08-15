from app_config import env_config as ec
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
from dataset.sale import model as schema
from model.sale_event import SaleEvent
from processor.inmemory.sale_processor import InmemorySaleProcessor
from processor.spark.sale_processor import SparkSaleProcessor


def _schema():
    return schema.get_struct_type()


SALE_DATASET = Dataset(
    name="Sale",
    dataframe=Dataframe(
        schema_factory=_schema,
        required_columns=schema.required_columns,
    ),
    event=Event(
        key_column=schema.model.order_id,
        converter=lambda row: SaleEvent.from_dict(row).to_dict(),
    ),
    audit=Audit(
        topic=ec.APP_STREAMING_AUDIT_TOPIC,
        archive_enabled=ec.APP_AUDIT_ARCHIVE_ENABLED,
    ),
    sources={
        "file": FileEndpoint(
            name="file",
            file_name="sale.csv",
            file_path=str(ec.ROOT / ec.RESOURCES_DIR / "sale.csv"),
        ),
        "messaging": MessagingEndpoint(
            name="messaging",
            topic=ec.APP_STREAMING_TOPIC,
            server=ec.APP_STREAMING_BOOTSTRAP_SERVERS,
            bootstrap_servers=ec.APP_STREAMING_BOOTSTRAP_SERVERS,
            checkpoint_path=f"{ec.APP_DATALAKE_SCHEME}://{ec.APP_DATALAKE_BUCKET_NAME}/checkpoints/{ec.APP_STREAMING_TOPIC}",
            starting_offsets=ec.APP_STREAMING_STARTING_OFFSETS,
        ),
    },
    destinations={
        "datalake": DataLakeEndpoint(name="datalake"),
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
            full_table_name=f"{ec.APP_DATAWAREHOUSE_NAME}.sale_table",
            preparing_sql_files={
                "truncate": "datawarehouse/sale/truncate_datawarehouse.sql"
            },
            analysis_sql_files={
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
