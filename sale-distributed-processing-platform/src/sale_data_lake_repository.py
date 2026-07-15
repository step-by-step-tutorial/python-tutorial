
from pyspark.sql import DataFrame

from src import config


class SaleDataLakeRepository:
    def replace_curated_sale_data(
        self,
        transformed_sale_dataframe: DataFrame,
    ) -> None:
        (
            transformed_sale_dataframe
            .write
            .mode("overwrite")
            .partitionBy("year", "month", "country")
            .parquet(config.build_sale_data_lake_output_uri())
        )
