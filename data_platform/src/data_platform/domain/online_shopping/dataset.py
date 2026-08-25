from data_platform.config.keys import Key
from data_platform.config.main_settings import settings as main_settings

from data_platform.domain.online_shopping.attribute import (
    ONLINE_SHOPPING_ATTRIBUTE as columns,
)
from data_platform.domain.online_shopping.inmemory_analyzer import (
    InmemoryOnlineShoppingAnalyzer,
)
from data_platform.cleaners import CleanerChain, DropDuplicatesCleaner, NumericColumnCleaner, ToDatetimeCleaner
from data_platform.enrichers import CopyColumnEnricher, DatetimePartEnricher, EnricherChain, PercentageEnricher
from data_platform.validators import NonNegativeValidator, NotNullValidator, PositiveValidator, RequiredColumnsValidator, ValidatorChain
from data_platform.ingestion.rest_api_csv_ingestor import RestApiCsvIngestor
from data_platform.model import (
    DataFrameModel,
    DataLakeEndpoint,
    WarehouseEndpoint,
    DatabaseEndpoint,
    Dataset,
    PipelineFlow,
    RestApiEndpoint,
)
from data_platform.persistence.data_lake_repository import DataLakeRepository
from data_platform.persistence.inmemory_database_repository import (
    PandasDatabaseRepository,
)
from data_platform.persistence.repository_data_exposer import RepositoryDataExposer
from data_platform.presentation.dataframe_display import show_map_of_dataframe
from data_platform.registry.endpoint_registry import audit_endpoint, endpoint_registry
from data_platform.service.dataframe_analysis_service import DataFrameAnalyzer

ONLINE_SHOPPING_DATASET = Dataset(
    name="online_shopping",
    dataframe=DataFrameModel(
        required_columns=frozenset(
            {
                columns.order_id,
                columns.order_date,
                columns.sales_channel,
                columns.country,
                columns.product_name,
                columns.unit_price,
                columns.quantity,
                columns.total_amount,
            }
        )
    ),
    audit=endpoint_registry.get_item(audit_endpoint.pipeline_name),
    endpoints={
        Key.ONLINE_SHOPPING_REST_API: (
            RestApiEndpoint(
                name=Key.ONLINE_SHOPPING_REST_API,
                url=f"{main_settings.api["test_data"].url.rstrip('/')}/datasets/online_shopping/download?format=csv",
            )
        ),
        Key.ONLINE_SHOPPING_DATA_LAKE: (
            DataLakeEndpoint(
                name=Key.ONLINE_SHOPPING_DATA_LAKE,
                connection_name=Key.ONLINE_SHOPPING_DATA_LAKE,
                bucket_name=main_settings.data_lake[Key.PLATFORM_DATA_LAKE].bucket_name,
                scheme=main_settings.data_lake[Key.PLATFORM_DATA_LAKE].scheme,
            )
        ),
        Key.ONLINE_SHOPPING_DATABASE: (
            DatabaseEndpoint(
                name=Key.ONLINE_SHOPPING_DATABASE,
                connection_name=Key.ONLINE_SHOPPING_DATABASE,
                schema="online_shopping",
                stage_table_name="online_shopping_stage",
                full_stage_table_name="online_shopping.online_shopping_stage",
                table_names=["online_shopping.online_shopping_stage"],
                create_sql_files={
                    "create": "database/online_shopping/create_tables.sql"
                },
                truncate_sql_files={
                    "truncate": "database/online_shopping/truncate_stage.sql"
                },
                query_sql_files={"select_all": "database/select_all.sql"},
            )
        ),
        Key.ONLINE_SHOPPING_WAREHOUSE: (
            WarehouseEndpoint(
                name=Key.ONLINE_SHOPPING_WAREHOUSE,
                connection_name=Key.ONLINE_SHOPPING_WAREHOUSE,
                schema=main_settings.warehouse[
                    Key.ONLINE_SHOPPING_WAREHOUSE
                ].database_name,
                table_name="online_shopping_table",
                full_table_name=f"{main_settings.warehouse[Key.ONLINE_SHOPPING_WAREHOUSE].database_name}.online_shopping_table",
                create_sql_files={
                    "create_database": "warehouse/online_shopping/create_database.sql",
                    "create_table": "warehouse/online_shopping/create_table.sql",
                },
                truncate_sql_files={
                    "truncate": "warehouse/online_shopping/truncate_warehouse.sql"
                },
                query_sql_files={
                    "select_all": "warehouse/select_all.sql",
                    "revenue_by_country": "warehouse/online_shopping/select_revenue_by_country.sql",
                },
            )
        ),
    },
    flow=PipelineFlow(
        repository=DataLakeRepository(
            DataLakeEndpoint(
                name=Key.ONLINE_SHOPPING_DATA_LAKE,
                connection_name=Key.ONLINE_SHOPPING_DATA_LAKE,
                bucket_name=main_settings.data_lake[
                    Key.PLATFORM_DATA_LAKE
                ].bucket_name,
                scheme=main_settings.data_lake[Key.PLATFORM_DATA_LAKE].scheme,
            )
        ),
        ingestors=(
            RestApiCsvIngestor(
                RestApiEndpoint(
                    name=Key.ONLINE_SHOPPING_REST_API,
                    url=f"{main_settings.api["test_data"].url.rstrip('/')}/datasets/online_shopping/download?format=csv",
                )
            ),
        ),
        cleaner=CleanerChain((
            DropDuplicatesCleaner(columns.order_id),
            ToDatetimeCleaner(columns.order_date),
            ToDatetimeCleaner(columns.estimated_delivery_date),
            NumericColumnCleaner(columns.customer_id),
            NumericColumnCleaner(columns.unit_price),
            NumericColumnCleaner(columns.quantity),
            NumericColumnCleaner(columns.subtotal),
            NumericColumnCleaner(columns.discount_percent),
            NumericColumnCleaner(columns.shipping_cost),
            NumericColumnCleaner(columns.tax_amount),
            NumericColumnCleaner(columns.total_amount),
            NumericColumnCleaner(columns.delivery_days),
        )),
        validator=ValidatorChain((
            RequiredColumnsValidator((columns.order_id, columns.order_date, columns.quantity, columns.unit_price, columns.total_amount)),
            NotNullValidator(columns.order_id),
            NotNullValidator(columns.order_date),
            PositiveValidator(columns.quantity),
            NonNegativeValidator(columns.unit_price),
            NonNegativeValidator(columns.total_amount),
        )),
        enricher=EnricherChain((
            PercentageEnricher(columns.subtotal, columns.discount_percent, columns.discount_amount),
            CopyColumnEnricher(columns.total_amount, columns.net_revenue, decimals=2),
            DatetimePartEnricher(columns.order_date, "year", columns.year),
            DatetimePartEnricher(columns.order_date, "month", columns.month),
        )),
        exposers=(
            RepositoryDataExposer((
                PandasDatabaseRepository(
                    DatabaseEndpoint(
                        name=Key.ONLINE_SHOPPING_DATABASE,
                        connection_name=Key.ONLINE_SHOPPING_DATABASE,
                        schema="online_shopping",
                        stage_table_name="online_shopping_stage",
                        full_stage_table_name="online_shopping.online_shopping_stage",
                        table_names=["online_shopping.online_shopping_stage"],
                        create_sql_files={
                            "create": "database/online_shopping/create_tables.sql"
                        },
                        truncate_sql_files={
                            "truncate": "database/online_shopping/truncate_stage.sql"
                        },
                        query_sql_files={"select_all": "database/select_all.sql"},
                    )
                ).replace,
            )),
        ),
        analyzers=(
            DataFrameAnalyzer(
                DataLakeRepository(
                    DataLakeEndpoint(
                        name=Key.ONLINE_SHOPPING_DATA_LAKE,
                        connection_name=Key.ONLINE_SHOPPING_DATA_LAKE,
                        bucket_name=main_settings.data_lake[
                            Key.PLATFORM_DATA_LAKE
                        ].bucket_name,
                        scheme=main_settings.data_lake[Key.PLATFORM_DATA_LAKE].scheme,
                    )
                ).find,
                InmemoryOnlineShoppingAnalyzer(),
                show_map_of_dataframe,
            ),
        ),
    ),
)
