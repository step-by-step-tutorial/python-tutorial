from pyspark.sql import DataFrame

from app_config import env_config as ec


def overwrite(dataframe: DataFrame, ) -> None:
    (
        dataframe.write
        .mode("overwrite")
        .partitionBy("year", "month", "country")
        .parquet(ec.build_sale_datalake_output_uri())
    )
