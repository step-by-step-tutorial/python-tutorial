from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType

APP_NAME = "Tutorial: DataFrame Basic Operation"
MASTER_URL = "spark://localhost:7077"
DRIVER_HOST = "host.docker.internal"
DRIVER_BIND_ADDRESS = "0.0.0.0"
TABLE_NAME = "person_table"


def create_session() -> SparkSession | None:
    """
    Create and return a Spark session between local machine and dockerized instance of Spark.

    :return: Spark session
    :exception: SparkSession creation failed.
    """
    try:
        session = SparkSession.builder \
            .appName(APP_NAME) \
            .master(MASTER_URL) \
            .config("spark.driver.host", DRIVER_HOST) \
            .config("spark.driver.bindAddress", DRIVER_BIND_ADDRESS) \
            .getOrCreate()
        session.sparkContext.setLogLevel("WARN")
        print(f"Application [{APP_NAME}] established a connection to Spark at [{DRIVER_HOST}]")
        return session
    except Exception as e:
        print(
            f"Application [{APP_NAME}] could not established a connection to Spark at [{DRIVER_HOST}] due to {str(e)}")
        return None


def get_schema() -> StructType:
    """Define and return the Person schema for the DataFrame."""
    schema = StructType([
        StructField("ID", IntegerType(), True),
        StructField("Salutation", StringType(), True),
        StructField("FirstName", StringType(), True),
        StructField("LastName", StringType(), True),
        StructField("DateOfBirth", DateType(), True),
        StructField("Gender", StringType(), True),
        StructField("MaritalStatus", StringType(), True),
        StructField("BirthNationality", StringType(), True),
        StructField("CurrentNationality", StringType(), True),
        StructField("Country", StringType(), True),
        StructField("Province", StringType(), True),
        StructField("City", StringType(), True),
        StructField("ZipCode", StringType(), True),
        StructField("Street", StringType(), True),
        StructField("HouseNumber", IntegerType(), True),
        StructField("MobilePhone", StringType(), True),
        StructField("EmailAddress", StringType(), True),
        StructField("JobTitle", StringType(), True),
        StructField("FieldOfStudy", StringType(), True),
        StructField("AcademicDegree", StringType(), True),
    ])
    return schema


def insert(session: SparkSession, schema: StructType, data) -> DataFrame | None:
    """
    Create a DataFrame and temp view to input data.

    :param session: Spark Session
    :param schema: StructType include column name and column type
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
        return session.table(TABLE_NAME) \
            .select("*") \
            .where(col("ID") == row_id)
    except Exception as e:
        print(f"Selecting data from {TABLE_NAME} failed due to {str(e)}")
        return None
