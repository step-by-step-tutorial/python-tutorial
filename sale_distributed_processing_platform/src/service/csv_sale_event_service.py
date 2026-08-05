import csv
import logging
from pathlib import Path

from app_config import env_config as ec
from app_config.dataframe_schema import SALE_COLUMNS
from model.sale_event import SaleEvent
from streaming.sale_event_producer import SaleEventProducer
from util.csv_utils import convert_to_integer, convert_to_optional_float, normalize_optional_text

logger = logging.getLogger(__name__)


def publish_sale_events(file_name: str) -> int:
    if file_name is None:
        raise ValueError("Cannot publish sale events because the input file name is None.")

    file_path = ec.resolve(Path(ec.RESOURCES_DIR)) / file_name

    if not file_path.exists():
        raise FileNotFoundError(f"Cannot publish sale events because the file does not exist: {file_path}")

    producer = SaleEventProducer()
    published_event_count = 0

    logger.info("Reading sale events from %s", file_path)

    with file_path.open(mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            sale_event = create_sale_event(row)
            producer.publish_sale_event(sale_event.to_dict())
            published_event_count += 1

    producer.flush()

    logger.info("Published %s sale events to Kafka topic %s", published_event_count, ec.KAFKA_TOPIC)

    return published_event_count


def create_sale_event(row: dict[str, str]) -> SaleEvent:
    return SaleEvent(
        order_id=convert_to_integer(row.get(SALE_COLUMNS.ORDER_ID)),
        customer_name=row[SALE_COLUMNS.CUSTOMER_NAME],
        product_name=row[SALE_COLUMNS.PRODUCT_NAME],
        category=row[SALE_COLUMNS.CATEGORY],
        quantity=convert_to_optional_float(row.get(SALE_COLUMNS.QUANTITY)),
        unit_price=convert_to_optional_float(row.get(SALE_COLUMNS.UNIT_PRICE)),
        order_date=normalize_optional_text(row.get(SALE_COLUMNS.ORDER_DATE)),
        country=row[SALE_COLUMNS.COUNTRY],
    )