import config
from csv_file_service import CsvFileService
from sales_data_cleaning_service import SalesDataCleaningService
from sales_data_transformation_service import SalesDataTransformationService
from postgres_sales_repository import PostgresSalesRepository
from minio_data_lake_service import MinioDataLakeService
from clickhouse_sales_repository import ClickHouseSalesRepository


class SalesEtlPipelineService:
    def run_pipeline(self) -> None:
        csv_file_service = CsvFileService()
        sales_data_cleaning_service = SalesDataCleaningService()
        sales_data_transformation_service = SalesDataTransformationService()

        sales_dataframe = csv_file_service.load_csv_file(config.CSV_FILE_PATH)

        cleaned_sales_dataframe = sales_data_cleaning_service.clean_sales_data(
            sales_dataframe
        )

        transformed_sales_dataframe = (
            sales_data_transformation_service.transform_sales_data(
                cleaned_sales_dataframe
            )
        )

        postgres_sales_repository = PostgresSalesRepository(config.POSTGRES_URL)
        postgres_sales_repository.load_sales_data(transformed_sales_dataframe)

        minio_data_lake_service = MinioDataLakeService(
            endpoint=config.MINIO_ENDPOINT,
            access_key=config.MINIO_ACCESS_KEY,
            secret_key=config.MINIO_SECRET_KEY,
            bucket_name=config.MINIO_BUCKET,
        )

        minio_data_lake_service.upload_parquet_file(
            dataframe=transformed_sales_dataframe,
            local_file_path=config.PARQUET_FILE_PATH,
            object_key="cleaned/sales/cleaned_sales_data.parquet",
        )

        sales_warehouse_dataframe = (
            sales_data_transformation_service.build_sales_warehouse_dataframe(
                transformed_sales_dataframe
            )
        )

        clickhouse_sales_repository = ClickHouseSalesRepository(
            host=config.CLICKHOUSE_HOST,
            port=config.CLICKHOUSE_PORT,
            database=config.CLICKHOUSE_DATABASE,
            username=config.CLICKHOUSE_USERNAME,
            password=config.CLICKHOUSE_PASSWORD,
        )

        clickhouse_sales_repository.load_sales_fact_data(
            sales_warehouse_dataframe
        )

        print(clickhouse_sales_repository.get_revenue_by_category())
        print(clickhouse_sales_repository.get_revenue_by_country())