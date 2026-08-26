from test_data.config.config_utils import read_config
from test_data.generator.row_generator import RowGenerator
from test_data.model.schemas import Dataset
from test_data.writer.writer_registry import WriterRegistry
import logging

logger = logging.getLogger(__name__)


class DatasetGenerator:

    def __init__(self, config_name: str) -> None:
        self.config = read_config(config_name)
        logger.info("Loaded dataset configuration: dataset=%s rows=%s destinations=%s", self.config.name, self.config.row_count, self.config.destinations)
        self.row_generator = RowGenerator(self.config, self.config.columns)
        self.writers = WriterRegistry()

    def write(self) -> Dataset:
        logger.info("Generating dataset: dataset=%s rows=%s", self.config.name, self.config.row_count)
        self.writers.write_all(self.row_generator.generate_rows(), self.config)
        logger.info("Dataset generation completed: dataset=%s rows=%s", self.config.name, self.config.row_count)
        return Dataset(name=self.config.name, config=self.config)
