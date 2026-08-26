import os
from dataclasses import dataclass


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
