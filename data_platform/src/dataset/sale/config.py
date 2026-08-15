import dataset.sale.model as schema
from app_config import env_config as ec
from dataset.definition import (
    Audit,
    DatabaseConnection,
    Dataset,
    Destination,
    Datalake,
    DataWarehouse,
    FileSource,
    Dataframe,
    Event,
    Messaging,
    Source,
    StageDatabase,
)
from processor.inmemory.sale_processor import InmemorySaleProcessor
from processor.distributed.sale_processor import DistributedSaleProcessor
from model.sale_event import SaleEvent
from util.file_utils import read_text_file

SALE_DATASET = Dataset(
    name="Sale",
    dataframe=Dataframe(
        schema=schema.struct_type,
        required_columns=schema.required_columns,
    ),
    event=Event(
        key_column=schema.model.ORDER_ID,
        converter=lambda row: SaleEvent.from_dict(row).to_dict(),
    ),
    messaging=Messaging(
        server=ec.APP_STREAMING_BOOTSTRAP_SERVERS,
        bootstrap_servers=ec.APP_STREAMING_BOOTSTRAP_SERVERS,
        topic=ec.APP_STREAMING_TOPIC,
        checkpoint_path=f"{ec.APP_DATALAKE_SCHEME}://{ec.APP_DATALAKE_BUCKET_NAME}/checkpoints/{ec.APP_STREAMING_TOPIC}",
        starting_offsets=ec.APP_STREAMING_STARTING_OFFSETS,
    ),
    audit=Audit(
        topic=ec.APP_STREAMING_AUDIT_TOPIC,
        archive_enabled=ec.APP_AUDIT_ARCHIVE_ENABLED,
    ),
    source=Source(
        file=FileSource(
            file_name="sale.csv",
            file_path=str(ec.ROOT / ec.RESOURCES_DIR / "sale.csv"),
        )
    ),
    destination=Destination(
        datalake=Datalake(bucket_name=ec.APP_DATALAKE_BUCKET_NAME),
        database=StageDatabase(
            connection=DatabaseConnection(
                server=ec.APP_DATABASE_HOST,
                port=ec.APP_DATABASE_PORT,
                database_name=ec.APP_DATABASE_NAME,
                user=ec.APP_DATABASE_USER,
                password=ec.APP_DATABASE_PASSWORD,
                driver=ec.APP_DATABASE_DRIVER,
                jdbc_url=ec.APP_DATABASE_JDBC_URL,
            ),
            table_name="sale.sale_stage",
            before_load_sql_files=("database/sale/truncate_stage.sql",),
            after_load_sql_files=(
                "database/sale/upsert_customer.sql",
                "database/sale/upsert_product.sql",
                "database/sale/upsert_order.sql",
                "database/sale/upsert_order_item.sql",
            ),
        ),
        datawarehouse=DataWarehouse(
            connection=DatabaseConnection(
                server=ec.APP_DATAWAREHOUSE_HOST,
                port=ec.APP_DATAWAREHOUSE_PORT,
                database_name=ec.APP_DATAWAREHOUSE_NAME,
                user=ec.APP_DATAWAREHOUSE_USER,
                password=ec.APP_DATAWAREHOUSE_PASSWORD,
                jdbc_url=f"jdbc:clickhouse://{ec.APP_DATAWAREHOUSE_HOST}:{ec.APP_DATAWAREHOUSE_PORT}/{ec.APP_DATAWAREHOUSE_NAME}",
            ),
            table_name="sale_table",
            full_table_name=f"{ec.APP_DATAWAREHOUSE_NAME}.sale_table",
            preparing_sql_files={
                "truncate": read_text_file("datawarehouse/sale/truncate_datawarehouse.sql")
            },
            analysis_sql_files={
                "revenue_by_category": read_text_file("datawarehouse/sale/select_revenue_by_category.sql"),
                "revenue_by_country": read_text_file("datawarehouse/sale/select_revenue_by_country.sql"),
            },
        ),
    ),
    processors={
        "inmemory": InmemorySaleProcessor(),
        "spark": DistributedSaleProcessor()
    },
)
