import dataset.sale.model as schema
from app_config import env_config as ec
from dataset.definition import (
    DatabaseConnection,
    Dataset,
    Destination,
    Datalake,
    DataWarehouse,
    FileSource,
    Source,
    StageDatabase,
    Streaming,
)
from dataset.sale.inmemory_processor import InmemorySaleProcessor
from dataset.sale.spark_processor import SparkSaleProcessor
from model.sale_event import SaleEvent
from util.file_utils import read_text_file

SALE_DATASET = Dataset(
    name="Sale",
    dataframe_schema=schema.struct_type,
    required_columns=schema.required_columns,
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
            columns=schema.all_columns,
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
            columns=schema.all_columns,
            preparing_sql_files={
                "truncate": read_text_file("datawarehouse/sale/truncate_datawarehouse.sql")
            },
            analysis_sql_files={
                "revenue_by_category": read_text_file("datawarehouse/sale/select_revenue_by_category.sql"),
                "revenue_by_country": read_text_file("datawarehouse/sale/select_revenue_by_country.sql"),
            },
        ),
    ),
    streaming=Streaming(
        server=ec.APP_STREAMING_BOOTSTRAP_SERVERS,
        bootstrap_servers=ec.APP_STREAMING_BOOTSTRAP_SERVERS,
        topic=ec.APP_STREAMING_TOPIC,
        consumer_group=ec.APP_STREAMING_CONSUMER_GROUP,
        checkpoint_path=f"{ec.APP_DATALAKE_SCHEME}://{ec.APP_DATALAKE_BUCKET_NAME}/checkpoints/{ec.APP_STREAMING_TOPIC}",
        starting_offsets=ec.APP_STREAMING_STARTING_OFFSETS,
        audit_topic=ec.APP_STREAMING_AUDIT_TOPIC,
        audit_consumer_group=ec.APP_STREAMING_AUDIT_CONSUMER_GROUP,
        dead_letter_topic=ec.APP_STREAMING_AUDIT_DEAD_LETTER_TOPIC,
    ),
    processors={
        "inmemory": InmemorySaleProcessor(),
        "spark": SparkSaleProcessor()
    },
    event_key_column=schema.model.ORDER_ID,
    event_converter=lambda row: SaleEvent.from_dict(row).to_dict(),
)
