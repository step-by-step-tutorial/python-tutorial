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

csv_path = "/resources/persons.csv"
print(f"Reading CSV file from {csv_path}")
csv = session.read.options(header=True, inferSchema=True).csv(csv_path)
csv.createOrReplaceTempView("persons")
csv.show(5)

session.stop()
print("Spark session closed.")
