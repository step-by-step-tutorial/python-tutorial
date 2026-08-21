from config_utils import read_config
from row_generator import RowGenerator
from schemas import Dataset
from writer_registry import WriterRegistry


class DatasetGenerator:

    def __init__(self, config_name: str) -> None:
        self.config = read_config(config_name)
        self.row_generator = RowGenerator(self.config, self.config.columns)
        self.writers = WriterRegistry()

    def write(self) -> Dataset:
        self.writers.write_all(self.row_generator.generate_rows(), self.config)
        return Dataset(name=self.config.name, config=self.config)
