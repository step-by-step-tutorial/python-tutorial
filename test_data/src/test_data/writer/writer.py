import logging
from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence

from test_data.connector.kafka_connector import publish
from test_data.model.config_model import ConfigModel
from test_data.model.settings_model import SettingsModel
from test_data.repository.database_repository import DatabaseRepository
from test_data.util.csv_utils import write_csv
from test_data.util.json_utils import write_json
from test_data.util.xml_utils import write_xml

logger = logging.getLogger(__name__)


class Writer(ABC):
    name: str

    @abstractmethod
    def write(self, rows: Sequence[Mapping[str, str]], config: ConfigModel) -> None:
        raise NotImplementedError


class CsvWriter(Writer):
    name = "csv"

    def write(self, rows: Sequence[Mapping[str, str]], config: ConfigModel) -> None:
        output_path = write_csv(config.output_file(self.name), config.column_names, rows)
        logger.info("CSV output written to %s", output_path)


class JsonWriter(Writer):
    name = "json"

    def write(self, rows: Sequence[Mapping[str, str]], config: ConfigModel) -> None:
        output_path = write_json(config.output_file(self.name), rows)
        logger.info("JSON output written to %s", output_path)


class XmlWriter(Writer):
    name = "xml"

    def write(self, rows: Sequence[Mapping[str, str]], config: ConfigModel) -> None:
        output_path = write_xml(config.output_file(self.name), config.column_names, rows)
        logger.info("XML output written to %s", output_path)


class DatabaseWriter(Writer):
    name = "database"

    def __init__(self, settings: SettingsModel) -> None:
        self._settings = settings

    def write(self, rows: Sequence[Mapping[str, str]], config: ConfigModel) -> None:
        repository = DatabaseRepository(self._settings.database_url, schema=self._settings.database_schema)
        repository.write_rows(table_name=config.table_name, headers=config.column_names, rows=rows)
        logger.info("Database output written to table %s.%s", self._settings.database_schema, config.table_name)


class KafkaWriter(Writer):
    name = "kafka"

    def __init__(self, settings: SettingsModel) -> None:
        self._settings = settings

    def write(self, rows: Sequence[Mapping[str, str]], config: ConfigModel) -> None:
        publish(
            self._settings.kafka_bootstrap_servers,
            config.kafka_topic,
            rows,
            config.kafka_key_column,
            self._settings.kafka_flush_timeout_seconds,
        )
        logger.info("Kafka output written: rows=%s topic=%s", len(rows), config.kafka_topic)
