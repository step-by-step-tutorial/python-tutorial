from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from test_data.config import settings as env_config
from test_data.repository.database_repository import DatabaseRepository
from test_data.connector.kafka_connector import create_producer
from test_data.util.csv_utils import write_csv
from test_data.util.json_utils import write_json
from test_data.util.kafka_utils import handle_delivery
from test_data.util.output_format_utils import output_file_name
from test_data.util.xml_utils import write_xml

logger = logging.getLogger(__name__)


class Writer(ABC):
    name: str

    @abstractmethod
    def write(self, rows: Sequence[Mapping[str, str]], config: Any) -> None:
        raise NotImplementedError


class CsvWriter(Writer):
    name = "csv"

    def write(self, rows: Sequence[Mapping[str, str]], config: Any) -> None:
        output_path = write_csv(
            env_config.OUTPUT_DIR / output_file_name(config.output_name, self.name), config.column_names, rows
        )
        logger.info("CSV output written to %s", output_path)


class JsonWriter(Writer):
    name = "json"

    def write(self, rows: Sequence[Mapping[str, str]], config: Any) -> None:
        output_path = write_json(env_config.OUTPUT_DIR / output_file_name(config.output_name, self.name), rows)
        logger.info("JSON output written to %s", output_path)


class XmlWriter(Writer):
    name = "xml"

    def write(self, rows: Sequence[Mapping[str, str]], config: Any) -> None:
        output_path = write_xml(
            env_config.OUTPUT_DIR / output_file_name(config.output_name, self.name), config.column_names, rows
        )
        logger.info("XML output written to %s", output_path)


class DatabaseWriter(Writer):
    name = "database"

    def write(self, rows: Sequence[Mapping[str, str]], config: Any) -> None:
        repository = DatabaseRepository(env_config.DATABASE_URL)
        table_name = Path(config.output_name).stem
        repository.write_rows(table_name=table_name, headers=config.column_names, rows=rows)
        logger.info("Database output written to table %s", table_name)


class KafkaWriter(Writer):
    name = "kafka"

    def write(self, rows: Sequence[Mapping[str, str]], config: Any) -> None:
        topic_name = config.kafka_topic
        producer = create_producer()
        for row in rows:
            producer.produce(
                topic=topic_name,
                key=str(row[config.kafka_key_column]),
                value=json.dumps(dict(row), ensure_ascii=False).encode("utf-8"),
                on_delivery=handle_delivery,
            )
            producer.poll(0)

        producer.flush()
        logger.info(f"Kafka output written {len(rows)} to topic {topic_name}")


class WriterRegistry:
    def __init__(self) -> None:
        writers = [
            CsvWriter(),
            JsonWriter(),
            XmlWriter(),
            DatabaseWriter(),
            KafkaWriter(),
        ]
        self._writers = {writer.name: writer for writer in writers}

    def write_all(self, rows: Iterable[Mapping[str, str]], config: Any) -> None:
        row_list = [dict(row) for row in rows]
        for name in config.destinations:
            self._writers[name].write(row_list, config)
