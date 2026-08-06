from typing import Any

from factory import datalake_connection_factory


def get_bucket_names(client: Any) -> list[str]:
    buckets = client.list_buckets().get("Buckets", [])
    return [bucket["Name"] for bucket in buckets]


def bucket_list() -> list[str]:
    with datalake_connection_factory.create_connection() as client:
        return get_bucket_names(client)


def bucket_exists(bucket_name: str) -> bool:
    with datalake_connection_factory.create_connection() as client:
        return bucket_name in get_bucket_names(client)


def create_bucket_if_not_exists(bucket_name: str) -> None:
    with datalake_connection_factory.create_connection() as client:
        if bucket_name not in get_bucket_names(client):
            client.create_bucket(Bucket=bucket_name)
