from data_platform.config.keys import Key
from data_platform.config.main_settings import settings as main_settings
from data_platform.domain.sale.attribute import SALE_ATTRIBUTE
from data_platform.domain.sale.warehouse_analyzer import WarehouseSaleAnalyzer
from data_platform.domain.sale.inmemory_analyzer import InmemorySaleAnalyzer
from data_platform.cleaners import (
    CastColumnCleaner,
    CleanerChain,
    DropDuplicatesCleaner,
    FillMissingByColumnAverageCleaner,
    FillMissingByGroupAverageCleaner,
    NumericColumnCleaner,
    ToDatetimeCleaner,
)
from data_platform.enrichers import DatetimePartEnricher, EnricherChain, MultiplyColumnsEnricher
from data_platform.validators import (
    NonNegativeValidator,
    NotNullValidator,
    PositiveValidator,
    RequiredColumnsValidator,
    ValidatorChain,
)
from data_platform.domain.sale.spark_schema import build_schema
from data_platform.ingestion.csv_file_ingestor import CsvFileIngestor
from data_platform.model import (
    DataFrameModel,
    DataLakeEndpoint,
    WarehouseEndpoint,
    DatabaseEndpoint,
    Dataset,
    FileEndpoint,
    MessagingEndpoint,
    PipelineFlow,
    RestApiEndpoint,
)
from data_platform.persistence.data_lake_repository import DataLakeRepository
from data_platform.persistence.inmemory_warehouse_repository import (
    PandasWarehouseRepository,
)
from data_platform.persistence.inmemory_database_repository import (
    PandasDatabaseRepository,
)
from data_platform.persistence.repository_data_exposer import RepositoryDataExposer
from data_platform.presentation.dataframe_display import show_map_of_dataframe
from data_platform.registry.endpoint_registry import audit_endpoint, endpoint_registry
from data_platform.service.warehouse_analysis_service import WarehouseAnalyzer
from data_platform.service.dataframe_analysis_service import DataFrameAnalyzer

SALE_DATASET = Dataset(
    name="sale",
    dataframe=DataFrameModel(
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
    audit=endpoint_registry.get_item(audit_endpoint.pipeline_name),
    endpoints={
        Key.SALE_CSV_FILE: (
            FileEndpoint(
                name=Key.SALE_CSV_FILE,
                file_name="sale.csv",
                file_path=str(
                    main_settings.app.root
                    / main_settings.app.resources_dir
                    / "sale.csv"
                ),
            )
        ),
        Key.SALE_REST_API: (
            RestApiEndpoint(
                name=Key.SALE_REST_API,
                url=f"{main_settings.api['test_data'].url.rstrip('/')}/datasets/sale.json/download?format=json",
            )
        ),
        Key.SALE_KAFKA_CONSUMER: (
            MessagingEndpoint(
                name=Key.SALE_KAFKA_CONSUMER,
                connection_name=Key.SALE_KAFKA_CONSUMER,
                channel_name=main_settings.messaging[
                    Key.SALE_KAFKA_CONSUMER
                ].channel_name,
                bootstrap_servers=main_settings.messaging[
                    Key.SALE_KAFKA_CONSUMER
                ].bootstrap_servers,
                starting_offsets=main_settings.messaging[
                    Key.SALE_KAFKA_CONSUMER
                ].starting_offsets,
            )
        ),
        Key.SALE_KAFKA_PRODUCER: (
            MessagingEndpoint(
                name=Key.SALE_KAFKA_PRODUCER,
                connection_name=Key.SALE_KAFKA_PRODUCER,
                channel_name=main_settings.messaging[
                    Key.SALE_KAFKA_PRODUCER
                ].channel_name,
                bootstrap_servers=main_settings.messaging[
                    Key.SALE_KAFKA_PRODUCER
                ].bootstrap_servers,
            )
        ),
        Key.SALE_DATA_LAKE: (
            DataLakeEndpoint(
                name=Key.SALE_DATA_LAKE,
                connection_name=Key.SALE_DATA_LAKE,
                bucket_name=main_settings.data_lake[Key.SALE_DATA_LAKE].bucket_name,
                scheme=main_settings.data_lake[Key.SALE_DATA_LAKE].scheme,
            )
        ),
        Key.SALE_DATABASE: (
            DatabaseEndpoint(
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
            )
        ),
        Key.SALE_WAREHOUSE: (
            WarehouseEndpoint(
                name=Key.SALE_WAREHOUSE,
                connection_name=Key.SALE_WAREHOUSE,
                schema=main_settings.warehouse[
                    Key.SALE_WAREHOUSE
                ].database_name,
                table_name="sale_table",
                full_table_name=f"{main_settings.warehouse[Key.SALE_WAREHOUSE].database_name}.sale_table",
                create_sql_files={
                    "create_database": "warehouse/sale/create_database.sql",
                    "create_table": "warehouse/sale/create_table.sql",
                },
                truncate_sql_files={
                    "truncate": "warehouse/sale/truncate_warehouse.sql"
                },
                query_sql_files={
                    "select_all": "warehouse/select_all.sql",
                    "revenue_by_category": "warehouse/sale/select_revenue_by_category.sql",
                    "revenue_by_country": "warehouse/sale/select_revenue_by_country.sql",
                },
            )
        ),
    },
    flow=PipelineFlow(
        repository=DataLakeRepository(
            DataLakeEndpoint(
                name=Key.SALE_DATA_LAKE,
                connection_name=Key.SALE_DATA_LAKE,
                bucket_name=main_settings.data_lake[Key.SALE_DATA_LAKE].bucket_name,
                scheme=main_settings.data_lake[Key.SALE_DATA_LAKE].scheme,
            )
        ),
        ingestors=(
            CsvFileIngestor(
                FileEndpoint(
                    name=Key.SALE_CSV_FILE,
                    file_name="sale.csv",
                    file_path=str(
                        main_settings.app.root
                        / main_settings.app.resources_dir
                        / "sale.csv"
                    ),
                )
            ),
        ),
        cleaner=CleanerChain((
            DropDuplicatesCleaner(SALE_ATTRIBUTE.order_id),
            NumericColumnCleaner(SALE_ATTRIBUTE.quantity, default_value=1.0),
            NumericColumnCleaner(SALE_ATTRIBUTE.unit_price),
            FillMissingByGroupAverageCleaner(SALE_ATTRIBUTE.category, SALE_ATTRIBUTE.unit_price),
            FillMissingByColumnAverageCleaner(SALE_ATTRIBUTE.unit_price),
            ToDatetimeCleaner(SALE_ATTRIBUTE.order_date),
            CastColumnCleaner(SALE_ATTRIBUTE.order_id, "int64"),
            CastColumnCleaner(SALE_ATTRIBUTE.quantity, "float64"),
            CastColumnCleaner(SALE_ATTRIBUTE.unit_price, "float64"),
        )),
        validator=ValidatorChain((
            RequiredColumnsValidator((
                SALE_ATTRIBUTE.order_id, SALE_ATTRIBUTE.quantity,
                SALE_ATTRIBUTE.unit_price, SALE_ATTRIBUTE.order_date,
            )),
            NotNullValidator(SALE_ATTRIBUTE.order_date),
            PositiveValidator(SALE_ATTRIBUTE.quantity),
            NonNegativeValidator(SALE_ATTRIBUTE.unit_price),
        )),
        enricher=EnricherChain((
            MultiplyColumnsEnricher(SALE_ATTRIBUTE.quantity, SALE_ATTRIBUTE.unit_price, SALE_ATTRIBUTE.total_price),
            DatetimePartEnricher(SALE_ATTRIBUTE.order_date, "year", SALE_ATTRIBUTE.year),
            DatetimePartEnricher(SALE_ATTRIBUTE.order_date, "month", SALE_ATTRIBUTE.month),
        )),
        exposers=(
            RepositoryDataExposer((
                PandasDatabaseRepository(
                    (
                        DatabaseEndpoint(
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
                            create_sql_files={
                                "create": "database/sale/create_tables.sql"
                            },
                            truncate_sql_files={
                                "truncate": "database/sale/truncate_stage.sql"
                            },
                            write_sql_files={
                                "customer": "database/sale/upsert_customer.sql",
                                "product": "database/sale/upsert_product.sql",
                                "order": "database/sale/upsert_order.sql",
                                "order_item": "database/sale/upsert_order_item.sql",
                            },
                            query_sql_files={"select_all": "database/select_all.sql"},
                        )
                    )
                ).replace,
            )),
            RepositoryDataExposer((
                PandasWarehouseRepository(
                    (
                        WarehouseEndpoint(
                            name=Key.SALE_WAREHOUSE,
                            connection_name=Key.SALE_WAREHOUSE,
                            schema=main_settings.warehouse[
                                Key.SALE_WAREHOUSE
                            ].database_name,
                            table_name="sale_table",
                            full_table_name=f"{main_settings.warehouse[Key.SALE_WAREHOUSE].database_name}.sale_table",
                            create_sql_files={
                                "create_database": "warehouse/sale/create_database.sql",
                                "create_table": "warehouse/sale/create_table.sql",
                            },
                            truncate_sql_files={
                                "truncate": "warehouse/sale/truncate_warehouse.sql"
                            },
                            query_sql_files={
                                "select_all": "warehouse/select_all.sql",
                                "revenue_by_category": "warehouse/sale/select_revenue_by_category.sql",
                                "revenue_by_country": "warehouse/sale/select_revenue_by_country.sql",
                            },
                        )
                    )
                ).replace,
            )),
        ),
        analyzers=(
            DataFrameAnalyzer(
                (
                    DataLakeRepository(
                        (
                            DataLakeEndpoint(
                                name=Key.SALE_DATA_LAKE,
                                connection_name=Key.SALE_DATA_LAKE,
                                bucket_name=main_settings.data_lake[
                                    Key.SALE_DATA_LAKE
                                ].bucket_name,
                                scheme=main_settings.data_lake[
                                    Key.SALE_DATA_LAKE
                                ].scheme,
                            )
                        )
                    )
                ).find,
                InmemorySaleAnalyzer(),
                show_map_of_dataframe,
            ),
            WarehouseAnalyzer(
                PandasWarehouseRepository(
                    (
                        WarehouseEndpoint(
                            name=Key.SALE_WAREHOUSE,
                            connection_name=Key.SALE_WAREHOUSE,
                            schema=main_settings.warehouse[
                                Key.SALE_WAREHOUSE
                            ].database_name,
                            table_name="sale_table",
                            full_table_name=f"{main_settings.warehouse[Key.SALE_WAREHOUSE].database_name}.sale_table",
                            create_sql_files={
                                "create_database": "warehouse/sale/create_database.sql",
                                "create_table": "warehouse/sale/create_table.sql",
                            },
                            truncate_sql_files={
                                "truncate": "warehouse/sale/truncate_warehouse.sql"
                            },
                            query_sql_files={
                                "select_all": "warehouse/select_all.sql",
                                "revenue_by_category": "warehouse/sale/select_revenue_by_category.sql",
                                "revenue_by_country": "warehouse/sale/select_revenue_by_country.sql",
                            },
                        )
                    )
                ),
                WarehouseSaleAnalyzer(),
                show_map_of_dataframe,
            ),
        ),
    ),
)
