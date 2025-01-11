import pandas as pd
from pyspark.sql import SparkSession

APP_NAME = "Tutorial: DataFrame Basic Operation"
MASTER_URL = "spark://localhost:7077"
DRIVER_HOST = "host.docker.internal"
DRIVER_BIND_ADDRESS = "0.0.0.0"

session = SparkSession.builder \
    .appName(APP_NAME) \
    .master(MASTER_URL) \
    .config("spark.driver.host", DRIVER_HOST) \
    .config("spark.driver.bindAddress", DRIVER_BIND_ADDRESS) \
    .getOrCreate()
print("Spark session established.")

csv = pd.read_csv('../resources/persons.csv')
data_frame = session.createDataFrame(csv)
data_frame.show()

session.stop()
print("Spark session closed.")
