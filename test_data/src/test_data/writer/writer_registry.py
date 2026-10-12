import logging
from collections.abc import Iterable, Mapping

from test_data.model import ConfigModel
from test_data.writer.writer import CsvWriter, DatabaseWriter, JsonWriter, KafkaWriter, XmlWriter

logger = logging.getLogger(__name__)


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

    def write_all(self, rows: Iterable[Mapping[str, str]], config: ConfigModel) -> None:
        """Write the rows to every configured destination; raise after all of them ran if any failed."""
        row_list = [dict(row) for row in rows]
        logger.info("Writing dataset outputs: dataset=%s rows=%s destinations=%s",
                    config.name, len(row_list), config.destinations)
        failures: dict[str, str] = {}
        for name in config.destinations:
            writer = self._writers.get(name)
            if writer is None:
                failures[name] = "writer is not registered"
                logger.error("Writer '%s' is not registered; continuing with next writer.", name)
                continue
            try:
                writer.write(row_list, config)
            except Exception as error:
                failures[name] = str(error)
                logger.error("Writer '%s' failed due to %s; continuing with next writer.", name, error)

        if failures:
            raise WriterError(failures)
        logger.info("Dataset outputs completed: dataset=%s rows=%s", config.name, len(row_list))


class WriterError(RuntimeError):
    def __init__(self, failures: dict[str, str]) -> None:
        self.failures = failures
        details = "; ".join(f"{name}: {reason}" for name, reason in failures.items())
        super().__init__(f"Writing outputs failed for {len(failures)} destination(s): {details}")
