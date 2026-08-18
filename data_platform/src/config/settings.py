from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Mapping


@dataclass(frozen=True)
class AppSettings:
    dataset_name: str
    pipeline_type: str
    root: Path
    resources_dir: str
    output_dir: Path
    scripts_dir: Path
    spark_dir: Path
    data_file: str


@dataclass(frozen=True)
class DatabaseSettings:
    host: str
    port: int
    database_name: str
    user: str
    password: str
    driver: str
    jdbc_url: str
    sqlalchemy_url: str


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


@dataclass(frozen=True)
class DataWarehouseSettings:
    host: str
    port: int
    database_name: str
    user: str
    password: str
    jdbc_url: str


@dataclass(frozen=True)
class MessagingSettings:
    bootstrap_servers: str
    channel_name: str
    audit_channel_name: str
    starting_offsets: str


@dataclass(frozen=True)
class RestSettings:
    url: str
    method: str


@dataclass(frozen=True)
class SparkSettings:
    application_name: str
    master_url: str
    driver_host: str
    driver_bind_address: str
    buffer: str
    active_blocks: str
    threads_max: str
    max_total_tasks: str
    max_direct_memory_size: str


@dataclass(frozen=True)
class MainSettings:
    app: AppSettings
    database: Mapping[str, DatabaseSettings]
    datalake: Mapping[str, DataLakeSettings]
    datawarehouse: Mapping[str, DataWarehouseSettings]
    messaging: Mapping[str, MessagingSettings]
    rest: Mapping[str, RestSettings]
    spark: SparkSettings


app = AppSettings(
    dataset_name=os.getenv("DATASET_NAME", "Sale"),
    pipeline_type=os.getenv("PIPELINE_TYPE", "inmemory"),
    root=Path(os.getenv("ROOT", Path(__file__).resolve().parents[2])),
    resources_dir=os.getenv("RESOURCES_DIR", "resources"),
    output_dir=Path(os.getenv("OUTPUT_DIR", "output")),
    scripts_dir=Path(os.getenv("SCRIPTS_DIR", "scripts")),
    spark_dir=Path(os.getenv("SPARK_DIR", "spark")),
    data_file=os.getenv("DATA_FILE", "sale.csv"),
)

database = MappingProxyType(
    {
        "app.database": DatabaseSettings(
            host=os.getenv("APP_DATABASE_HOST", "localhost"),
            port=int(os.getenv("APP_DATABASE_PORT", "5432")),
            database_name=os.getenv("APP_DATABASE_NAME", "app_database"),
            user=os.getenv("APP_DATABASE_USER", "admin"),
            password=os.getenv("APP_DATABASE_PASSWORD", "admin"),
            driver=os.getenv("APP_DATABASE_DRIVER", "org.postgresql.Driver"),
            jdbc_url=os.getenv(
                "APP_DATABASE_JDBC_URL",
                "jdbc:postgresql://"
                f"{os.getenv('APP_DATABASE_HOST', 'localhost')}:"
                f"{os.getenv('APP_DATABASE_PORT', '5432')}/"
                f"{os.getenv('APP_DATABASE_NAME', 'app_database')}",
            ),
            sqlalchemy_url=os.getenv(
                "APP_DATABASE_SQLALCHEMY_URL",
                "postgresql+psycopg2://"
                f"{os.getenv('APP_DATABASE_USER', 'admin')}:"
                f"{os.getenv('APP_DATABASE_PASSWORD', 'admin')}@"
                f"{os.getenv('APP_DATABASE_HOST', 'localhost')}:"
                f"{os.getenv('APP_DATABASE_PORT', '5432')}/"
                f"{os.getenv('APP_DATABASE_NAME', 'app_database')}",
            ),
        ),
        "sale.database": DatabaseSettings(
            host=os.getenv("APP_SALE_DATABASE_HOST", "localhost"),
            port=int(os.getenv("APP_SALE_DATABASE_PORT", "5432")),
            database_name=os.getenv("APP_SALE_DATABASE_NAME", "app_database"),
            user=os.getenv("APP_SALE_DATABASE_USER", "admin"),
            password=os.getenv("APP_SALE_DATABASE_PASSWORD", "admin"),
            driver=os.getenv("APP_SALE_DATABASE_DRIVER", "org.postgresql.Driver"),
            jdbc_url=os.getenv(
                "APP_SALE_DATABASE_JDBC_URL",
                "jdbc:postgresql://"
                f"{os.getenv('APP_SALE_DATABASE_HOST', 'localhost')}:"
                f"{os.getenv('APP_SALE_DATABASE_PORT', '5432')}/"
                f"{os.getenv('APP_SALE_DATABASE_NAME', 'app_database')}",
            ),
            sqlalchemy_url=os.getenv(
                "APP_SALE_DATABASE_SQLALCHEMY_URL",
                "postgresql+psycopg2://"
                f"{os.getenv('APP_SALE_DATABASE_USER', 'admin')}:"
                f"{os.getenv('APP_SALE_DATABASE_PASSWORD', 'admin')}@"
                f"{os.getenv('APP_SALE_DATABASE_HOST', 'localhost')}:"
                f"{os.getenv('APP_SALE_DATABASE_PORT', '5432')}/"
                f"{os.getenv('APP_SALE_DATABASE_NAME', 'app_database')}",
            ),
        ),
        "house.database": DatabaseSettings(
            host=os.getenv("APP_HOUSE_DATABASE_HOST", "localhost"),
            port=int(os.getenv("APP_HOUSE_DATABASE_PORT", "5432")),
            database_name=os.getenv("APP_HOUSE_DATABASE_NAME", "app_database"),
            user=os.getenv("APP_HOUSE_DATABASE_USER", "admin"),
            password=os.getenv("APP_HOUSE_DATABASE_PASSWORD", "admin"),
            driver=os.getenv("APP_HOUSE_DATABASE_DRIVER", "org.postgresql.Driver"),
            jdbc_url=os.getenv(
                "APP_HOUSE_DATABASE_JDBC_URL",
                "jdbc:postgresql://"
                f"{os.getenv('APP_HOUSE_DATABASE_HOST', 'localhost')}:"
                f"{os.getenv('APP_HOUSE_DATABASE_PORT', '5432')}/"
                f"{os.getenv('APP_HOUSE_DATABASE_NAME', 'app_database')}",
            ),
            sqlalchemy_url=os.getenv(
                "APP_HOUSE_DATABASE_SQLALCHEMY_URL",
                "postgresql+psycopg2://"
                f"{os.getenv('APP_HOUSE_DATABASE_USER', 'admin')}:"
                f"{os.getenv('APP_HOUSE_DATABASE_PASSWORD', 'admin')}@"
                f"{os.getenv('APP_HOUSE_DATABASE_HOST', 'localhost')}:"
                f"{os.getenv('APP_HOUSE_DATABASE_PORT', '5432')}/"
                f"{os.getenv('APP_HOUSE_DATABASE_NAME', 'app_database')}",
            ),
        ),
        "audit.database": DatabaseSettings(
            host=os.getenv("APP_AUDIT_DATABASE_HOST", "localhost"),
            port=int(os.getenv("APP_AUDIT_DATABASE_PORT", "5432")),
            database_name=os.getenv("APP_AUDIT_DATABASE_NAME", "app_database"),
            user=os.getenv("APP_AUDIT_DATABASE_USER", "admin"),
            password=os.getenv("APP_AUDIT_DATABASE_PASSWORD", "admin"),
            driver=os.getenv("APP_AUDIT_DATABASE_DRIVER", "org.postgresql.Driver"),
            jdbc_url=os.getenv(
                "APP_AUDIT_DATABASE_JDBC_URL",
                "jdbc:postgresql://"
                f"{os.getenv('APP_AUDIT_DATABASE_HOST', 'localhost')}:"
                f"{os.getenv('APP_AUDIT_DATABASE_PORT', '5432')}/"
                f"{os.getenv('APP_AUDIT_DATABASE_NAME', 'app_database')}",
            ),
            sqlalchemy_url=os.getenv(
                "APP_AUDIT_DATABASE_SQLALCHEMY_URL",
                "postgresql+psycopg2://"
                f"{os.getenv('APP_AUDIT_DATABASE_USER', 'admin')}:"
                f"{os.getenv('APP_AUDIT_DATABASE_PASSWORD', 'admin')}@"
                f"{os.getenv('APP_AUDIT_DATABASE_HOST', 'localhost')}:"
                f"{os.getenv('APP_AUDIT_DATABASE_PORT', '5432')}/"
                f"{os.getenv('APP_AUDIT_DATABASE_NAME', 'app_database')}",
            ),
        ),
    }
)

datalake = MappingProxyType(
    {
        "app.datalake": DataLakeSettings(
            endpoint=os.getenv("APP_DATALAKE_ENDPOINT", "http://localhost:9000"),
            access_key=os.getenv("APP_DATALAKE_ACCESS_KEY", "admin"),
            secret_key=os.getenv("APP_DATALAKE_SECRET_KEY", "administrator"),
            bucket_name=os.getenv("APP_DATALAKE_BUCKET_NAME", "app-datalake"),
            audit_bucket_name=os.getenv("APP_DATALAKE_AUDIT_BUCKET_NAME", "app-datalake-audit"),
            scheme=os.getenv("APP_DATALAKE_SCHEME", "s3a"),
            environment=os.getenv("APP_DATALAKE_ENVIRONMENT", "dev"),
            checkpoint_path=os.getenv("APP_DATALAKE_CHECKPOINT_PATH", "s3a://app-datalake/checkpoints/sale-events"),
        ),
        "sale.datalake": DataLakeSettings(
            endpoint=os.getenv("APP_SALE_DATALAKE_ENDPOINT", "http://localhost:9000"),
            access_key=os.getenv("APP_SALE_DATALAKE_ACCESS_KEY", "admin"),
            secret_key=os.getenv("APP_SALE_DATALAKE_SECRET_KEY", "administrator"),
            bucket_name=os.getenv("APP_SALE_DATALAKE_BUCKET_NAME", "app-datalake"),
            audit_bucket_name=os.getenv("APP_SALE_DATALAKE_AUDIT_BUCKET_NAME", "app-datalake-audit"),
            scheme=os.getenv("APP_SALE_DATALAKE_SCHEME", "s3a"),
            environment=os.getenv("APP_SALE_DATALAKE_ENVIRONMENT", "dev"),
            checkpoint_path=os.getenv("APP_SALE_DATALAKE_CHECKPOINT_PATH", "s3a://app-datalake/checkpoints/sale-events"),
        ),
        "house.datalake": DataLakeSettings(
            endpoint=os.getenv("APP_HOUSE_DATALAKE_ENDPOINT", "http://localhost:9000"),
            access_key=os.getenv("APP_HOUSE_DATALAKE_ACCESS_KEY", "admin"),
            secret_key=os.getenv("APP_HOUSE_DATALAKE_SECRET_KEY", "administrator"),
            bucket_name=os.getenv("APP_HOUSE_DATALAKE_BUCKET_NAME", "app-datalake-house"),
            audit_bucket_name=os.getenv("APP_HOUSE_DATALAKE_AUDIT_BUCKET_NAME", "app-datalake-audit"),
            scheme=os.getenv("APP_HOUSE_DATALAKE_SCHEME", "s3a"),
            environment=os.getenv("APP_HOUSE_DATALAKE_ENVIRONMENT", "dev"),
            checkpoint_path=os.getenv("APP_HOUSE_DATALAKE_CHECKPOINT_PATH", "s3a://app-datalake/checkpoints/house-events"),
        ),
        "audit.datalake": DataLakeSettings(
            endpoint=os.getenv("APP_AUDIT_DATALAKE_ENDPOINT", "http://localhost:9000"),
            access_key=os.getenv("APP_AUDIT_DATALAKE_ACCESS_KEY", "admin"),
            secret_key=os.getenv("APP_AUDIT_DATALAKE_SECRET_KEY", "administrator"),
            bucket_name=os.getenv("APP_AUDIT_DATALAKE_BUCKET_NAME", "app-datalake-audit"),
            audit_bucket_name=os.getenv("APP_AUDIT_BUCKET_NAME", "app-datalake-audit"),
            scheme=os.getenv("APP_AUDIT_DATALAKE_SCHEME", "s3a"),
            environment=os.getenv("APP_AUDIT_DATALAKE_ENVIRONMENT", "dev"),
            checkpoint_path=os.getenv("APP_AUDIT_DATALAKE_CHECKPOINT_PATH", "s3a://app-datalake/checkpoints/audit-events"),
        ),
    }
)

datawarehouse = MappingProxyType(
    {
        "app.datawarehouse": DataWarehouseSettings(
            host=os.getenv("APP_DATAWAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("APP_DATAWAREHOUSE_PORT", "8123")),
            database_name=os.getenv("APP_DATAWAREHOUSE_NAME", "app_datawarehouse"),
            user=os.getenv("APP_DATAWAREHOUSE_USER", "admin"),
            password=os.getenv("APP_DATAWAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv(
                "APP_DATAWAREHOUSE_JDBC_URL",
                "jdbc:clickhouse://"
                f"{os.getenv('APP_DATAWAREHOUSE_HOST', 'localhost')}:"
                f"{os.getenv('APP_DATAWAREHOUSE_PORT', '8123')}/"
                f"{os.getenv('APP_DATAWAREHOUSE_NAME', 'app_datawarehouse')}",
            ),
        ),
        "sale.datawarehouse": DataWarehouseSettings(
            host=os.getenv("APP_SALE_DATAWAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("APP_SALE_DATAWAREHOUSE_PORT", "8123")),
            database_name=os.getenv("APP_SALE_DATAWAREHOUSE_NAME", "app_datawarehouse"),
            user=os.getenv("APP_SALE_DATAWAREHOUSE_USER", "admin"),
            password=os.getenv("APP_SALE_DATAWAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv(
                "APP_SALE_DATAWAREHOUSE_JDBC_URL",
                "jdbc:clickhouse://"
                f"{os.getenv('APP_SALE_DATAWAREHOUSE_HOST', 'localhost')}:"
                f"{os.getenv('APP_SALE_DATAWAREHOUSE_PORT', '8123')}/"
                f"{os.getenv('APP_SALE_DATAWAREHOUSE_NAME', 'app_datawarehouse')}",
            ),
        ),
        "house.datawarehouse": DataWarehouseSettings(
            host=os.getenv("APP_HOUSE_DATAWAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("APP_HOUSE_DATAWAREHOUSE_PORT", "8123")),
            database_name=os.getenv("APP_HOUSE_DATAWAREHOUSE_NAME", "app_datawarehouse"),
            user=os.getenv("APP_HOUSE_DATAWAREHOUSE_USER", "admin"),
            password=os.getenv("APP_HOUSE_DATAWAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv(
                "APP_HOUSE_DATAWAREHOUSE_JDBC_URL",
                "jdbc:clickhouse://"
                f"{os.getenv('APP_HOUSE_DATAWAREHOUSE_HOST', 'localhost')}:"
                f"{os.getenv('APP_HOUSE_DATAWAREHOUSE_PORT', '8123')}/"
                f"{os.getenv('APP_HOUSE_DATAWAREHOUSE_NAME', 'app_datawarehouse')}",
            ),
        ),
        "audit.datawarehouse": DataWarehouseSettings(
            host=os.getenv("APP_AUDIT_DATAWAREHOUSE_HOST", "localhost"),
            port=int(os.getenv("APP_AUDIT_DATAWAREHOUSE_PORT", "8123")),
            database_name=os.getenv("APP_AUDIT_DATAWAREHOUSE_NAME", "app_datawarehouse"),
            user=os.getenv("APP_AUDIT_DATAWAREHOUSE_USER", "admin"),
            password=os.getenv("APP_AUDIT_DATAWAREHOUSE_PASSWORD", "admin"),
            jdbc_url=os.getenv(
                "APP_AUDIT_DATAWAREHOUSE_JDBC_URL",
                "jdbc:clickhouse://"
                f"{os.getenv('APP_AUDIT_DATAWAREHOUSE_HOST', 'localhost')}:"
                f"{os.getenv('APP_AUDIT_DATAWAREHOUSE_PORT', '8123')}/"
                f"{os.getenv('APP_AUDIT_DATAWAREHOUSE_NAME', 'app_datawarehouse')}",
            ),
        ),
    }
)

messaging = MappingProxyType(
    {
        "sale": MessagingSettings(
            bootstrap_servers=os.getenv("APP_SALE_STREAMING_BOOTSTRAP_SERVERS", "localhost:9092"),
            channel_name=os.getenv("APP_SALE_CHANNEL_NAME", "sale-events"),
            audit_channel_name=os.getenv("APP_SALE_AUDIT_CHANNEL_NAME", "sale.audit.event.v1"),
            starting_offsets=os.getenv("APP_SALE_STREAMING_STARTING_OFFSETS", "earliest"),
        ),
        "house": MessagingSettings(
            bootstrap_servers=os.getenv("APP_HOUSE_STREAMING_BOOTSTRAP_SERVERS", "localhost:9092"),
            channel_name=os.getenv("APP_HOUSE_CHANNEL_NAME", "house-events"),
            audit_channel_name=os.getenv("APP_HOUSE_AUDIT_CHANNEL_NAME", "house.audit.event.v1"),
            starting_offsets=os.getenv("APP_HOUSE_STREAMING_STARTING_OFFSETS", "earliest"),
        ),
        "audit": MessagingSettings(
            bootstrap_servers=os.getenv("APP_AUDIT_STREAMING_BOOTSTRAP_SERVERS", "localhost:9092"),
            channel_name=os.getenv("APP_AUDIT_STREAM_CHANNEL_NAME", "audit-events"),
            audit_channel_name=os.getenv("APP_AUDIT_CHANNEL_NAME", "sale.audit.event.v1"),
            starting_offsets=os.getenv("APP_AUDIT_STREAMING_STARTING_OFFSETS", "earliest"),
        ),
    }
)

rest = MappingProxyType(
    {
        "sale": RestSettings(
            url=os.getenv("APP_SALE_REST_URL", "http://localhost:8080"),
            method=os.getenv("APP_SALE_REST_METHOD", "GET"),
        ),
        "house": RestSettings(
            url=os.getenv("APP_HOUSE_REST_URL", "http://localhost:8080"),
            method=os.getenv("APP_HOUSE_REST_METHOD", "GET"),
        ),
    }
)

spark = SparkSettings(
    application_name=os.getenv("SPARK_APPLICATION_NAME", "data_platform"),
    master_url=os.getenv("SPARK_MASTER_URL", "local[*]"),
    driver_host=os.getenv("SPARK_DRIVER_HOST", "127.0.0.1"),
    driver_bind_address=os.getenv("SPARK_DRIVER_BIND_ADDRESS", "127.0.0.1"),
    buffer=os.getenv("SPARK_BUFFER", "array"),
    active_blocks=os.getenv("SPARK_ACTIVE_BLOCKS", "1"),
    threads_max=os.getenv("SPARK_THREADS_MAX", "4"),
    max_total_tasks=os.getenv("SPARK_MAX_TOTAL_TASKS", "4"),
    max_direct_memory_size=os.getenv("MAX_DIRECT_MEMORY_SIZE", "2g"),
)

settings = MainSettings(
    app=app,
    database=database,
    datalake=datalake,
    datawarehouse=datawarehouse,
    messaging=messaging,
    rest=rest,
    spark=spark,
)
