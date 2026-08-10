import logging
from pathlib import Path

from app_config import env_config as ec
from converter.event_converter import conver_dict_event
from streaming.event_producer import EventProducer
from util.file_utils import absolute_path, read_csv_file
from util.string_utils import should_be_not_none

logger = logging.getLogger(__name__)


def publish(file_name: str) -> int:
    should_be_not_none(file_name, "file_name")
    csv_file_path = absolute_path(Path(ec.RESOURCES_DIR)) / file_name
    logger.info("Reading CSV file from %s", csv_file_path)

    producer = EventProducer()
    event_counter = read_csv_file(csv_file_path, lambda row: producer.publish(conver_dict_event(row).to_dict()))
    producer.flush()
    logger.info("Published %s events to streaming topic %s", event_counter, ec.STREAMING_TOPIC)

    return event_counter
