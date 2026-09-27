from dataclasses import dataclass


@dataclass(frozen=True)
class DataLakeConfig:
    endpoint: str
    access_key: str
    secret_key: str
    bucket_name: str
    object_prefix: str
