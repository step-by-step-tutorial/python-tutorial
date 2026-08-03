from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import DataFrame
from pyspark.sql import functions as sf


def read_sale_data_from_csv(connection: SparkSession | None, path, schema) -> DataFrame:
    if connection is None:
        raise ValueError("SparkSession connection cannot be None")
    return connection.read.option("header", "true").schema(schema).csv(path)


def transform_sale_data(dataframe: DataFrame, ) -> DataFrame:
    return (
        dataframe
        .withColumn("total_price", sf.round(sf.col("quantity") * sf.col("unit_price"), 2))
        .withColumn("year", sf.year("order_date"))
        .withColumn("month", sf.month("order_date"))
    )
