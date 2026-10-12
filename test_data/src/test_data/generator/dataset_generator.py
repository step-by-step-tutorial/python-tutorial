import logging
from pathlib import Path

from test_data.generator.row_generator import RowGenerator
from test_data.model.config_model import ConfigModel
from test_data.model.settings_model import SettingsModel
from test_data.writer.writer_registry import WriterRegistry

logger = logging.getLogger(__name__)


class DatasetGenerator:

    def __init__(self, config_name: str | Path, settings: SettingsModel) -> None:
        self.config = ConfigModel.from_file(config_name, settings)
        logger.info("Loaded dataset configuration: dataset=%s rows=%s destinations=%s",
                    self.config.name, self.config.row_count, self.config.destinations)
        self.row_generator = RowGenerator(self.config, settings)
        self.writers = WriterRegistry(settings)

    def write(self) -> ConfigModel:
        logger.info("Generating dataset: dataset=%s rows=%s", self.config.name, self.config.row_count)
        self.writers.write_all(self.row_generator.generate_rows(), self.config)
        logger.info("Dataset generation completed: dataset=%s rows=%s", self.config.name, self.config.row_count)
        return self.config
