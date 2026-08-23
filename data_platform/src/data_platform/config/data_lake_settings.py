import os
from dataclasses import dataclass
from types import MappingProxyType

from data_platform.config.keys import Key


@dataclass(frozen=True)
class DataLakeSettings:
    endpoint: str
    access_key: str
    secret_key: str
    bucket_name: str
    audit_bucket_name: str
    scheme: str
    environment: str
    checkpoint_path: str


data_lake = MappingProxyType(
    {
        Key.PLATFORM_DATA_LAKE: DataLakeSettings(
            endpoint=os.getenv("PLATFORM_DATA_LAKE_ENDPOINT", "http://localhost:9000"),
            access_key=os.getenv("PLATFORM_DATA_LAKE_ACCESS_KEY", "admin"),
            secret_key=os.getenv("PLATFORM_DATA_LAKE_SECRET_KEY", "administrator"),
            bucket_name=os.getenv("PLATFORM_DATA_LAKE_BUCKET_NAME", "app-datalake"),
            audit_bucket_name=os.getenv("PLATFORM_DATA_LAKE_AUDIT_BUCKET_NAME", "app-datalake-audit"),
            scheme=os.getenv("PLATFORM_DATA_LAKE_SCHEME", "s3a"),
            environment=os.getenv("PLATFORM_DATA_LAKE_ENVIRONMENT", "dev"),
            checkpoint_path=os.getenv("PLATFORM_DATA_LAKE_CHECKPOINT_PATH",
                                      "s3a://app-datalake/checkpoints/sale-events"),
        ),
        Key.SALE_DATA_LAKE: DataLakeSettings(
            endpoint=os.getenv("DATA_PLATFORM_SALE_DATA_LAKE_ENDPOINT", "http://localhost:9000"),
            access_key=os.getenv("DATA_PLATFORM_SALE_DATA_LAKE_ACCESS_KEY", "admin"),
            secret_key=os.getenv("DATA_PLATFORM_SALE_DATA_LAKE_SECRET_KEY", "administrator"),
            bucket_name=os.getenv("DATA_PLATFORM_SALE_DATA_LAKE_BUCKET_NAME", "app-datalake"),
            audit_bucket_name=os.getenv("DATA_PLATFORM_SALE_DATA_LAKE_AUDIT_BUCKET_NAME", "app-datalake-audit"),
            scheme=os.getenv("DATA_PLATFORM_SALE_DATA_LAKE_SCHEME", "s3a"),
            environment=os.getenv("DATA_PLATFORM_SALE_DATA_LAKE_ENVIRONMENT", "dev"),
            checkpoint_path=os.getenv("DATA_PLATFORM_SALE_DATA_LAKE_CHECKPOINT_PATH",
                                      "s3a://app-datalake/checkpoints/sale-events"),
        ),
        Key.HOUSE_DATA_LAKE: DataLakeSettings(
            endpoint=os.getenv("DATA_PLATFORM_HOUSE_DATA_LAKE_ENDPOINT", "http://localhost:9000"),
            access_key=os.getenv("DATA_PLATFORM_HOUSE_DATA_LAKE_ACCESS_KEY", "admin"),
            secret_key=os.getenv("DATA_PLATFORM_HOUSE_DATA_LAKE_SECRET_KEY", "administrator"),
            bucket_name=os.getenv("DATA_PLATFORM_HOUSE_DATA_LAKE_BUCKET_NAME", "app-datalake-house"),
            audit_bucket_name=os.getenv("DATA_PLATFORM_HOUSE_DATA_LAKE_AUDIT_BUCKET_NAME", "app-datalake-audit"),
            scheme=os.getenv("DATA_PLATFORM_HOUSE_DATA_LAKE_SCHEME", "s3a"),
            environment=os.getenv("DATA_PLATFORM_HOUSE_DATA_LAKE_ENVIRONMENT", "dev"),
            checkpoint_path=os.getenv("DATA_PLATFORM_HOUSE_DATA_LAKE_CHECKPOINT_PATH",
                                      "s3a://app-datalake/checkpoints/house-events"),
        ),
        Key.AUDIT_DATA_LAKE: DataLakeSettings(
            endpoint=os.getenv("DATA_PLATFORM_AUDIT_DATA_LAKE_ENDPOINT", "http://localhost:9000"),
            access_key=os.getenv("DATA_PLATFORM_AUDIT_DATA_LAKE_ACCESS_KEY", "admin"),
            secret_key=os.getenv("DATA_PLATFORM_AUDIT_DATA_LAKE_SECRET_KEY", "administrator"),
            bucket_name=os.getenv("DATA_PLATFORM_AUDIT_DATA_LAKE_BUCKET_NAME", "app-datalake-audit"),
            audit_bucket_name=os.getenv("DATA_PLATFORM_AUDIT_BUCKET_NAME", "app-datalake-audit"),
            scheme=os.getenv("DATA_PLATFORM_AUDIT_DATA_LAKE_SCHEME", "s3a"),
            environment=os.getenv("DATA_PLATFORM_AUDIT_DATA_LAKE_ENVIRONMENT", "dev"),
            checkpoint_path=os.getenv("DATA_PLATFORM_AUDIT_DATA_LAKE_CHECKPOINT_PATH",
                                      "s3a://app-datalake/checkpoints/audit-events"),
        ),
    }
)
