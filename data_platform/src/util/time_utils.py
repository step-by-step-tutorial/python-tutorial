import time
import logging

from datetime import datetime, UTC

logger = logging.getLogger(__name__)


def elapsed_milliseconds(started_at: float) -> int:
    return int((time.perf_counter() - started_at) * 1000)


def generate_ingestion_time() -> datetime:
    ingestion_time = datetime.now(UTC)
    logger.info("Generated ingestion time %s", ingestion_time.isoformat())
    return ingestion_time
