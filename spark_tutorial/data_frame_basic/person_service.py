from pyspark.sql import DataFrame
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StructType

TABLE_NAME = "person_table"


def insert(session: SparkSession, schema: StructType, data) -> DataFrame | None:
    """
    Create a DataFrame and temp view to input data.

    :param session: Spark Session
    :param schema: StructType includes column name and column type
    :param data: a list of data to insert
    :return: a DataFrame containing the data
    :exception: insert failed.
    """

    if session is None:
        raise ValueError("Spark session should not be null")
    if schema is None:
        raise ValueError("Schema should not be null")
    if data is None:
        raise ValueError("data should not be null")

    try:
        data_frame = session.createDataFrame(data, schema=schema)
        data_frame.createOrReplaceTempView(TABLE_NAME)
        print(f"{data_frame.count()} records inserted into {TABLE_NAME}")
        return data_frame
    except Exception as e:
        print(f"Inserting data to {TABLE_NAME} failed due to {str(e)}")
        return None


def select_by_id(session: SparkSession, row_id) -> DataFrame | None:
    """
    select a recorde of temp view by ID.

    :param session: Spark Session
    :param row_id: recorder id
    :return: DataFrame
    :exception: select failed.
    """

    if session is None:
        raise ValueError("Spark session should not be null")
    if row_id is None:
        raise ValueError("Row ID should not be null")

    try:
        data_frame = session.table(TABLE_NAME).select("*").where(col("ID") == row_id)
        print(f"Selecting data from {TABLE_NAME} by ID: {row_id}")
        return data_frame
    except Exception as e:
        print(f"Selecting data from {TABLE_NAME} failed due to {str(e)}")
        return None
