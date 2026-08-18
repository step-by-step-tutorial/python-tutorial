from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DataLakeSettings:
    endpoint: str
    access_key: str
    secret_key: str
    bucket_name: str
    audit_bucket_name: str
    scheme: str
    environment: str


sale_settings = DataLakeSettings(
    endpoint=os.getenv("APP_SALE_DATALAKE_ENDPOINT", "http://localhost:9000"),
    access_key=os.getenv("APP_SALE_DATALAKE_ACCESS_KEY", "admin"),
    secret_key=os.getenv("APP_SALE_DATALAKE_SECRET_KEY", "administrator"),
    bucket_name=os.getenv("APP_SALE_DATALAKE_BUCKET_NAME", "app-datalake"),
    audit_bucket_name=os.getenv("APP_SALE_DATALAKE_AUDIT_BUCKET_NAME", "app-datalake-audit"),
    scheme=os.getenv("APP_SALE_DATALAKE_SCHEME", "s3a"),
    environment=os.getenv("APP_SALE_DATALAKE_ENVIRONMENT", "dev"),
)
house_settings = DataLakeSettings(
    endpoint=os.getenv("APP_HOUSE_DATALAKE_ENDPOINT", "http://localhost:9000"),
    access_key=os.getenv("APP_HOUSE_DATALAKE_ACCESS_KEY", "admin"),
    secret_key=os.getenv("APP_HOUSE_DATALAKE_SECRET_KEY", "administrator"),
    bucket_name=os.getenv("APP_HOUSE_DATALAKE_BUCKET_NAME", "app-datalake-house"),
    audit_bucket_name=os.getenv("APP_HOUSE_DATALAKE_AUDIT_BUCKET_NAME", "app-datalake-audit"),
    scheme=os.getenv("APP_HOUSE_DATALAKE_SCHEME", "s3a"),
    environment=os.getenv("APP_HOUSE_DATALAKE_ENVIRONMENT", "dev"),
)
audit_settings = DataLakeSettings(
    endpoint=os.getenv("APP_AUDIT_DATALAKE_ENDPOINT", "http://localhost:9000"),
    access_key=os.getenv("APP_AUDIT_DATALAKE_ACCESS_KEY", "admin"),
    secret_key=os.getenv("APP_AUDIT_DATALAKE_SECRET_KEY", "administrator"),
    bucket_name=os.getenv("APP_AUDIT_DATALAKE_BUCKET_NAME", "app-datalake-audit"),
    audit_bucket_name=os.getenv("APP_AUDIT_ARCHIVE_BUCKET_NAME", "app-datalake-audit"),
    scheme=os.getenv("APP_AUDIT_DATALAKE_SCHEME", "s3a"),
    environment=os.getenv("APP_AUDIT_DATALAKE_ENVIRONMENT", "dev"),
)

settings = sale_settings
