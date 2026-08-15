from config.app import settings as app_settings
from config.audit import settings as audit_settings
from config.database import settings as database_settings
from config.datalake import settings as datalake_settings
from config.datawarehouse import settings as datawarehouse_settings
from config.messaging import settings as messaging_settings
from config.spark import settings as spark_settings

DATASET_NAME = app_settings.dataset_name
PIPELINE_TYPE = app_settings.pipeline_type
ROOT = app_settings.root
RESOURCES_DIR = app_settings.resources_dir
OUTPUT_DIR = app_settings.output_dir
SCRIPTS_DIR = app_settings.scripts_dir
SPARK_DIR = app_settings.spark_dir
DATA_FILE = app_settings.data_file

SPARK_APPLICATION_NAME = spark_settings.application_name
SPARK_MASTER_URL = spark_settings.master_url
SPARK_DRIVER_HOST = spark_settings.driver_host
SPARK_DRIVER_BIND_ADDRESS = spark_settings.driver_bind_address
SPARK_BUFFER = spark_settings.buffer
SPARK_ACTIVE_BLOCKS = spark_settings.active_blocks
SPARK_THREADS_MAX = spark_settings.threads_max
SPARK_MAX_TOTAL_TASKS = spark_settings.max_total_tasks
MAX_DIRECT_MEMORY_SIZE = spark_settings.max_direct_memory_size

APP_DATABASE_HOST = database_settings.host
APP_DATABASE_PORT = database_settings.port
APP_DATABASE_NAME = database_settings.database_name
APP_DATABASE_USER = database_settings.user
APP_DATABASE_PASSWORD = database_settings.password
APP_DATABASE_DRIVER = database_settings.driver
APP_DATABASE_JDBC_URL = database_settings.jdbc_url
APP_DATABASE_SQLALCHEMY_URL = database_settings.sqlalchemy_url

APP_DATALAKE_ENDPOINT = datalake_settings.endpoint
APP_DATALAKE_ACCESS_KEY = datalake_settings.access_key
APP_DATALAKE_SECRET_KEY = datalake_settings.secret_key
APP_DATALAKE_BUCKET_NAME = datalake_settings.bucket_name
APP_DATALAKE_AUDIT_BUCKET_NAME = datalake_settings.audit_bucket_name
APP_DATALAKE_SCHEME = datalake_settings.scheme
APP_DATALAKE_ENVIRONMENT = datalake_settings.environment

APP_DATAWAREHOUSE_HOST = datawarehouse_settings.host
APP_DATAWAREHOUSE_PORT = datawarehouse_settings.port
APP_DATAWAREHOUSE_NAME = datawarehouse_settings.database_name
APP_DATAWAREHOUSE_USER = datawarehouse_settings.user
APP_DATAWAREHOUSE_PASSWORD = datawarehouse_settings.password

APP_STREAMING_BOOTSTRAP_SERVERS = messaging_settings.bootstrap_servers
APP_STREAMING_TOPIC = messaging_settings.topic
APP_STREAMING_AUDIT_TOPIC = messaging_settings.audit_topic
APP_STREAMING_STARTING_OFFSETS = messaging_settings.starting_offsets
APP_STREAMING_CHECKPOINT_PATH = f"{APP_DATALAKE_SCHEME}://{APP_DATALAKE_BUCKET_NAME}/checkpoints/{APP_STREAMING_TOPIC}"

APP_AUDIT_ARCHIVE_ENABLED = audit_settings.archive_enabled
