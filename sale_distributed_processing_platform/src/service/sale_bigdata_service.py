from pyspark.sql import DataFrame, SparkSession


def read_sale_data_from_csv(connection: SparkSession | None, path, schema) -> DataFrame:
    if connection is None:
        raise ValueError("SparkSession connection cannot be None")
    return connection.read.option("header", "true").schema(schema).csv(path)
