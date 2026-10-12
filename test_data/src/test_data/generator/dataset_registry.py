import logging
from pathlib import Path

from test_data.config import settings as env_config
from test_data.model.schemas import ConfigModel, Dataset, DatasetMetadata
from test_data.util.file_utils import list_of_file_names

logger = logging.getLogger(__name__)


class DatasetNotFoundError(LookupError):
    pass


class DatasetRegistry:
    def __init__(self) -> None:
        self._datasets = {
            Path(name).stem: Dataset(name=Path(name).stem, config=ConfigModel.from_file(name))
            for name in list_of_file_names(env_config.CONFIG_DIR)
        }
        logger.info("Loaded dataset registry: datasets=%s", list(self._datasets))

    def get_all_datasets(self) -> list[Dataset]:
        return list(self._datasets.values())

    def get_all_names(self) -> list[str]:
        return list(self._datasets)

    def get_one(self, name: str) -> Dataset:
        try:
            return self._datasets[name]
        except KeyError as error:
            raise DatasetNotFoundError(f"Dataset {name} is not configured.") from error

    def get_all_metadata(self) -> list[DatasetMetadata]:
        return [DatasetMetadata.from_dataset(dataset) for dataset in self.get_all_datasets()]
