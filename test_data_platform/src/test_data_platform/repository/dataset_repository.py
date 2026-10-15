import logging

from test_data_platform.model.config_model import ConfigModel
from test_data_platform.model.dataset_metadata_model import DatasetMetadataModel
from test_data_platform.model.settings_model import SettingsModel
from test_data_platform.util.file_utils import list_file_names

logger = logging.getLogger(__name__)


class DatasetNotFoundError(LookupError):
    pass


class DatasetRepository:
    """The datasets configured in the config directory, by dataset name."""

    def __init__(self, settings: SettingsModel) -> None:
        self._settings = settings
        configs = (ConfigModel.from_file(name, settings) for name in list_file_names(settings.config_dir))
        self._configs = {config.dataset_name: config for config in configs}
        logger.info("Loaded datasets: datasets=%s", list(self._configs))

    def get_all(self) -> list[ConfigModel]:
        return list(self._configs.values())

    def get_all_names(self) -> list[str]:
        return list(self._configs)

    def get_one(self, name: str) -> ConfigModel:
        try:
            return self._configs[name]
        except KeyError as error:
            raise DatasetNotFoundError(f"Dataset {name} is not configured.") from error

    def get_all_metadata(self) -> list[DatasetMetadataModel]:
        return [DatasetMetadataModel.from_config(config, self._settings) for config in self.get_all()]
