from pyspark.sql import DataFrame, SparkSession

from factory import bigdata_engine_session_factory


def read_sale_data(path, schema) -> DataFrame:
    connection: SparkSession | None = None
    try:
        connection = bigdata_engine_session_factory.create_session()
        return connection.read.option("header", "true").schema(schema).csv(path)
    finally:
        if connection:
            connection.stop()
