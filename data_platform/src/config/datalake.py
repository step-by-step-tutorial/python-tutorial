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


settings = DataLakeSettings(
    endpoint=os.getenv("APP_DATALAKE_ENDPOINT", "http://localhost:9000"),
    access_key=os.getenv("APP_DATALAKE_ACCESS_KEY", "admin"),
    secret_key=os.getenv("APP_DATALAKE_SECRET_KEY", "administrator"),
    bucket_name=os.getenv("APP_DATALAKE_BUCKET_NAME", "app-datalake"),
    audit_bucket_name=os.getenv("APP_DATALAKE_AUDIT_BUCKET_NAME", "app-datalake-audit"),
    scheme=os.getenv("APP_DATALAKE_SCHEME", "s3a"),
    environment=os.getenv("APP_DATALAKE_ENVIRONMENT", "dev"),
)

