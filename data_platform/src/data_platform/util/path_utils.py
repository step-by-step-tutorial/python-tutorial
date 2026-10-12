from datetime import datetime
from uuid import UUID, uuid4

from data_platform.config.storage_environment import StorageEnvironment


def join_path(*parts: object) -> str:
    """Join path components using one canonical forward-slash separator."""
    return "/".join(str(part).strip("/") for part in parts if str(part).strip("/"))


def normalize_relative_path(path: str) -> str:
    return join_path(path)


def generate_relative_path(env: StorageEnvironment, ingestion_time: datetime, dataset_name: str) -> str:
    ingestion_id = ingestion_time.strftime("%Y%m%dT%H%M%S%fZ")
    return join_path(
        env.value,
        dataset_name.lower(),
        f"ingestion_year={ingestion_time.year}",
        f"ingestion_month={ingestion_time.month:02d}",
        f"ingestion_day={ingestion_time.day:02d}",
        f"ingestion_time={ingestion_id}",
    )


def generate_object_key(relative_path: str, filename: str) -> str:
    return join_path(relative_path, filename)


def generate_data_object_key(
        relative_path: str,
        file_extension: str = "parquet",
        object_id: UUID | None = None,
) -> str:
    suffix = file_extension.strip(".")
    return generate_object_key(relative_path, f"part-{object_id or uuid4()}.{suffix}")


def generate_audit_event_key(event_time: datetime, pipeline_name: str, pipeline_id: str, event_id: UUID) -> str:
    return generate_object_key(
        join_path(
            "events",
            f"event_date={event_time.date().isoformat()}",
            f"pipeline_name={pipeline_name}",
            f"pipeline_id={pipeline_id}",
        ),
        f"{event_id}.json",
    )


def generate_audit_manifest_key(event_time: datetime, pipeline_name: str, pipeline_id: str) -> str:
    return generate_object_key(
        join_path(
            "manifests",
            f"event_date={event_time.date().isoformat()}",
            f"pipeline_name={pipeline_name}",
            f"pipeline_id={pipeline_id}",
        ),
        "pipeline_manifest.json",
    )


def generate_full_path(bucket_name: str, relative_path: str, scheme: str = "s3a") -> str:
    return f"{scheme}://{join_path(bucket_name, relative_path)}"


def generate_checkpoint_path(bucket_name: str, checkpoint_name: str, scheme: str = "s3a") -> str:
    return generate_full_path(bucket_name, join_path("checkpoints", checkpoint_name), scheme)
