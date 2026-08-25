from datetime import datetime
from data_platform.config.data_lake_environment import StorageEnvironment
from data_platform.model.endpoints import DataLakeEndpoint


def generate_relative_path(
        env: StorageEnvironment,
        ingestion_time: datetime,
        dataset_name: str
) -> str:
    ingestion_id = ingestion_time.strftime("%Y%m%dT%H%M%S%fZ")

    return (
        f"{env.value}/{dataset_name.lower()}/"
        f"ingestion_year={ingestion_time.year}/"
        f"ingestion_month={ingestion_time.month:02d}/"
        f"ingestion_day={ingestion_time.day:02d}/"
        f"ingestion_time={ingestion_id}"
    )


def generate_full_path(bucket_name: str, relative_path: str) -> str:
    return f"s3a://{bucket_name.strip()}/{relative_path.strip('/')}"


def generate_data_lake_path(endpoint: DataLakeEndpoint, relative_path: str) -> str:
    return f"{endpoint.scheme}://{endpoint.bucket_name.strip()}/{relative_path.strip('/')}"


def extract_filename(path: str) -> str:
    return path.rstrip("/").split("/")[-1]
