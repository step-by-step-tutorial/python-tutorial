import time
from datetime import datetime, UTC


def elapsed_milliseconds(started_at: float) -> int:
    return int((time.perf_counter() - started_at) * 1000)


def generate_ingestion_time() -> datetime:
    return datetime.now(UTC)
