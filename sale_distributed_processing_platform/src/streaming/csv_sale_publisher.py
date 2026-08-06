import logging
from pathlib import Path
from typing import Any

from app_config import env_config as ec
from model.sale_event import from_dict
from streaming.event_producer import EventProducer
from util.file_utils import build_absolute_path, read_csv_file
from util.string_utils import should_be_not_none

logger = logging.getLogger(__name__)


def publish_data(file_name: str) -> int:
    should_be_not_none("file_name", file_name)
    csv_file_path = build_absolute_path(Path(ec.RESOURCES_DIR)) / file_name
    logger.info("Reading CSV file from %s", csv_file_path)

    producer = EventProducer()
    event_counter = read_csv_file(
        csv_file_path,
        lambda row: publish_event(producer, row)
    )
    producer.flush()
    logger.info("Published %s sale events to Kafka topic %s", event_counter, ec.KAFKA_TOPIC)

    return event_counter


def publish_event(producer: EventProducer, data: dict[str | Any, str | Any]):
    event = from_dict(data)
    producer.publish(event.to_dict())
