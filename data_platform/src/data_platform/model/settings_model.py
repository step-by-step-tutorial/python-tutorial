import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from data_platform.config.key import Key

DEFAULT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_USER = "admin"
DEFAULT_PASSWORD = "admin"
DEFAULT_DATA_LAKE_SECRET_KEY = "administrator"


@dataclass(frozen=True)
class AppSettingsModel:
    root: Path
    resources_dir: str
    scripts_dir: Path

    @classmethod
    def from_env(cls, environ: Mapping[str, str]) -> "AppSettingsModel":
        return cls(
            root=Path(environ.get("ROOT", DEFAULT_ROOT)),
            resources_dir=environ.get("RESOURCES_DIR", "resources"),
            scripts_dir=Path(environ.get("SCRIPTS_DIR", "scripts")),
        )

    def resource_path(self, file_name: str) -> Path:
        return self.root / self.resources_dir / file_name

    def script_path(self, file_name: str) -> Path:
        return self.root / self.scripts_dir / file_name


@dataclass(frozen=True)
class ApiSettingsModel:
    url: str

    @classmethod
    def from_env(cls, prefix: str, environ: Mapping[str, str], url: str) -> "ApiSettingsModel":
        return cls(url=environ.get(f"{prefix}_URL", url))

    def dataset_download_url(self, dataset_name: str, file_format: str = "csv") -> str:
        return f"{self.url.rstrip('/')}/datasets/{dataset_name.lower()}/download?format={file_format}"


@dataclass(frozen=True)
class DatabaseSettingsModel:
    host: str
    port: int
    database_name: str
    user: str
    password: str
    driver: str
    jdbc_url: str
    sqlalchemy_url: str

    @classmethod
    def from_env(cls, prefix: str, environ: Mapping[str, str]) -> "DatabaseSettingsModel":
        host = environ.get(f"{prefix}_HOST", "localhost")
        port = environ.get(f"{prefix}_PORT", "5432")
        database_name = environ.get(f"{prefix}_NAME", "app_database")
        user = environ.get(f"{prefix}_USER", DEFAULT_USER)
        password = environ.get(f"{prefix}_PASSWORD", DEFAULT_PASSWORD)
        return cls(
            host=host,
            port=int(port),
            database_name=database_name,
            user=user,
            password=password,
            driver=environ.get(f"{prefix}_DRIVER", "org.postgresql.Driver"),
            jdbc_url=environ.get(f"{prefix}_JDBC_URL", f"jdbc:postgresql://{host}:{port}/{database_name}"),
            sqlalchemy_url=environ.get(
                f"{prefix}_SQLALCHEMY_URL",
                f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database_name}",
            ),
        )


@dataclass(frozen=True)
class DataLakeSettingsModel:
    endpoint: str
    access_key: str
    secret_key: str
    bucket_name: str
    backup_bucket_name: str
    scheme: str

    @classmethod
    def from_env(cls, prefix: str, environ: Mapping[str, str], bucket_name: str) -> "DataLakeSettingsModel":
        return cls(
            endpoint=environ.get(f"{prefix}_ENDPOINT", "http://localhost:9000"),
            access_key=environ.get(f"{prefix}_ACCESS_KEY", DEFAULT_USER),
            secret_key=environ.get(f"{prefix}_SECRET_KEY", DEFAULT_DATA_LAKE_SECRET_KEY),
            bucket_name=environ.get(f"{prefix}_BUCKET_NAME", bucket_name),
            backup_bucket_name=environ.get("DATA_PLATFORM_DATALAKE_BACKUP_BUCKET_NAME", "backup"),
            scheme=environ.get(f"{prefix}_SCHEME", "s3a"),
        )


@dataclass(frozen=True)
class WarehouseSettingsModel:
    host: str
    port: int
    database_name: str
    user: str
    password: str
    jdbc_url: str

    @classmethod
    def from_env(cls, prefix: str, environ: Mapping[str, str]) -> "WarehouseSettingsModel":
        host = environ.get(f"{prefix}_HOST", "localhost")
        port = environ.get(f"{prefix}_PORT", "8123")
        database_name = environ.get(f"{prefix}_NAME", "app_warehouse")
        return cls(
            host=host,
            port=int(port),
            database_name=database_name,
            user=environ.get(f"{prefix}_USER", DEFAULT_USER),
            password=environ.get(f"{prefix}_PASSWORD", DEFAULT_PASSWORD),
            jdbc_url=environ.get(f"{prefix}_JDBC_URL", f"jdbc:clickhouse://{host}:{port}/{database_name}"),
        )


@dataclass(frozen=True)
class MessagingSettingsModel:
    bootstrap_servers: str
    channel_name: str
    starting_offsets: str

    @classmethod
    def from_env(cls, prefix: str, environ: Mapping[str, str], channel_name: str) -> "MessagingSettingsModel":
        return cls(
            bootstrap_servers=environ.get(f"{prefix}_STREAMING_BOOTSTRAP_SERVERS", "localhost:9092"),
            channel_name=environ.get(f"{prefix}_CHANNEL_NAME", channel_name),
            starting_offsets=environ.get(f"{prefix}_STREAMING_STARTING_OFFSETS", "earliest"),
        )


@dataclass(frozen=True)
class SparkSettingsModel:
    application_name: str
    master_url: str
    driver_host: str
    driver_bind_address: str
    buffer: str
    active_blocks: str
    threads_max: str
    max_total_tasks: str
    max_direct_memory_size: str

    @classmethod
    def from_env(cls, environ: Mapping[str, str]) -> "SparkSettingsModel":
        return cls(
            application_name=environ.get("SPARK_APPLICATION_NAME", "data_platform"),
            master_url=environ.get("SPARK_MASTER_URL", "local[*]"),
            driver_host=environ.get("SPARK_DRIVER_HOST", "127.0.0.1"),
            driver_bind_address=environ.get("SPARK_DRIVER_BIND_ADDRESS", "127.0.0.1"),
            buffer=environ.get("SPARK_BUFFER", "array"),
            active_blocks=environ.get("SPARK_ACTIVE_BLOCKS", "1"),
            threads_max=environ.get("SPARK_THREADS_MAX", "4"),
            max_total_tasks=environ.get("SPARK_MAX_TOTAL_TASKS", "4"),
            max_direct_memory_size=environ.get("MAX_DIRECT_MEMORY_SIZE", "2g"),
        )


@dataclass(frozen=True)
class SettingsModel:
    app: AppSettingsModel
    data_simulator: ApiSettingsModel
    database: Mapping[str, DatabaseSettingsModel]
    data_lake: Mapping[str, DataLakeSettingsModel]
    warehouse: Mapping[str, WarehouseSettingsModel]
    messaging: Mapping[str, MessagingSettingsModel]
    spark: SparkSettingsModel

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "SettingsModel":
        environ = os.environ if environ is None else environ
        return cls(
            app=AppSettingsModel.from_env(environ),
            data_simulator=ApiSettingsModel.from_env("DATA_SIMULATOR_API", environ, "http://localhost:8080"),
            database=MappingProxyType({
                Key.HOUSE_DATABASE: DatabaseSettingsModel.from_env("DATA_PLATFORM_HOUSE_DATABASE", environ),
                Key.ONLINE_SHOPPING_DATABASE: DatabaseSettingsModel.from_env(
                    "DATA_PLATFORM_ONLINE_SHOPPING_DATABASE", environ),
                Key.AUDIT_DATABASE: DatabaseSettingsModel.from_env("DATA_PLATFORM_AUDIT_DATABASE", environ),
            }),
            data_lake=MappingProxyType({
                Key.PLATFORM_DATA_LAKE: DataLakeSettingsModel.from_env(
                    "DATA_PLATFORM_DATALAKE", environ, "online-shopping"),
                Key.HOUSE_DATA_LAKE: DataLakeSettingsModel.from_env("DATA_PLATFORM_HOUSE_DATALAKE", environ, "house"),
                Key.ONLINE_SHOPPING_DATA_LAKE: DataLakeSettingsModel.from_env(
                    "DATA_PLATFORM_ONLINE_SHOPPING_DATALAKE", environ, "online-shopping"),
                Key.AUDIT_DATA_LAKE: DataLakeSettingsModel.from_env("DATA_PLATFORM_AUDIT_DATALAKE", environ, "audit"),
            }),
            warehouse=MappingProxyType({
                Key.HOUSE_WAREHOUSE: WarehouseSettingsModel.from_env("DATA_PLATFORM_HOUSE_WAREHOUSE", environ),
                Key.ONLINE_SHOPPING_WAREHOUSE: WarehouseSettingsModel.from_env(
                    "DATA_PLATFORM_ONLINE_SHOPPING_WAREHOUSE", environ),
                Key.AUDIT_WAREHOUSE: WarehouseSettingsModel.from_env("DATA_PLATFORM_AUDIT_WAREHOUSE", environ),
            }),
            messaging=MappingProxyType({
                Key.HOUSE_MESSAGING: MessagingSettingsModel.from_env("DATA_PLATFORM_HOUSE", environ, "house.events.v1"),
                Key.ONLINE_SHOPPING_MESSAGING: MessagingSettingsModel.from_env(
                    "DATA_PLATFORM_ONLINE_SHOPPING", environ, "online-shopping.events.v1"),
                Key.AUDIT_MESSAGING: MessagingSettingsModel.from_env(
                    "DATA_PLATFORM_AUDIT", environ, "audit.audit.events.v1"),
            }),
            spark=SparkSettingsModel.from_env(environ),
        )
