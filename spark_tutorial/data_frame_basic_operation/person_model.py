from pyspark.sql.types import StructType, StructField, StringType, IntegerType, DateType


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
