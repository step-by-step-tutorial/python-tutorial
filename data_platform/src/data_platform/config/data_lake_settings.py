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
            endpoint=os.getenv("DATA_PLATFORM_DATALAKE_ENDPOINT", "http://localhost:9000"),
            access_key=os.getenv("DATA_PLATFORM_DATALAKE_ACCESS_KEY", "admin"),
            secret_key=os.getenv("DATA_PLATFORM_DATALAKE_SECRET_KEY", "administrator"),
            bucket_name=os.getenv("DATA_PLATFORM_DATALAKE_BUCKET_NAME", "app-datalake"),
            audit_bucket_name=os.getenv("DATA_PLATFORM_DATALAKE_AUDIT_BUCKET_NAME", "app-datalake-audit"),
            scheme=os.getenv("DATA_PLATFORM_DATALAKE_SCHEME", "s3a"),
            environment=os.getenv("DATA_PLATFORM_DATALAKE_ENVIRONMENT", "dev"),
            checkpoint_path=os.getenv("DATA_PLATFORM_DATALAKE_CHECKPOINT_PATH",
                                      "s3a://app-datalake/checkpoints/events"),
        ),
        Key.HOUSE_DATA_LAKE: DataLakeSettings(
            endpoint=os.getenv("DATA_PLATFORM_HOUSE_DATALAKE_ENDPOINT", "http://localhost:9000"),
            access_key=os.getenv("DATA_PLATFORM_HOUSE_DATALAKE_ACCESS_KEY", "admin"),
            secret_key=os.getenv("DATA_PLATFORM_HOUSE_DATALAKE_SECRET_KEY", "administrator"),
            bucket_name=os.getenv("DATA_PLATFORM_HOUSE_DATALAKE_BUCKET_NAME", "app-datalake-house"),
            audit_bucket_name=os.getenv("DATA_PLATFORM_HOUSE_DATALAKE_AUDIT_BUCKET_NAME", "app-datalake-audit"),
            scheme=os.getenv("DATA_PLATFORM_HOUSE_DATALAKE_SCHEME", "s3a"),
            environment=os.getenv("DATA_PLATFORM_HOUSE_DATALAKE_ENVIRONMENT", "dev"),
            checkpoint_path=os.getenv("DATA_PLATFORM_HOUSE_DATALAKE_CHECKPOINT_PATH",
                                      "s3a://app-datalake/checkpoints/house-events"),
        ),
        Key.AUDIT_DATA_LAKE: DataLakeSettings(
            endpoint=os.getenv("DATA_PLATFORM_AUDIT_DATALAKE_ENDPOINT", "http://localhost:9000"),
            access_key=os.getenv("DATA_PLATFORM_AUDIT_DATALAKE_ACCESS_KEY", "admin"),
            secret_key=os.getenv("DATA_PLATFORM_AUDIT_DATALAKE_SECRET_KEY", "administrator"),
            bucket_name=os.getenv("DATA_PLATFORM_AUDIT_DATALAKE_BUCKET_NAME", "app-datalake-audit"),
            audit_bucket_name=os.getenv("DATA_PLATFORM_AUDIT_BUCKET_NAME", "app-datalake-audit"),
            scheme=os.getenv("DATA_PLATFORM_AUDIT_DATALAKE_SCHEME", "s3a"),
            environment=os.getenv("DATA_PLATFORM_AUDIT_DATALAKE_ENVIRONMENT", "dev"),
            checkpoint_path=os.getenv("DATA_PLATFORM_AUDIT_DATALAKE_CHECKPOINT_PATH",
                                      "s3a://app-datalake/checkpoints/audit-events"),
        ),
    }
)

