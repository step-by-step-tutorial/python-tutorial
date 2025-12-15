from pyspark.sql import SparkSession

APP_NAME = "Tutorial: DataFrame Basic Operation"
# MASTER_URL = "spark://localhost:7077"
MASTER_URL = "local[*]"
DRIVER_HOST = "host.docker.internal"
DRIVER_BIND_ADDRESS = "0.0.0.0"

session = SparkSession.builder \
    .appName(APP_NAME) \
    .master(MASTER_URL) \
    .config("spark.driver.host", DRIVER_HOST) \
    .config("spark.driver.bindAddress", DRIVER_BIND_ADDRESS) \
    .getOrCreate()
print("Spark session established.")

data_frame = session.read.options(header=True, inferSchema=True).csv("../resources/persons.csv")
data_frame.createOrReplaceTempView("persons")
data_frame.show(5)

session.stop()
print("Spark session closed.")
