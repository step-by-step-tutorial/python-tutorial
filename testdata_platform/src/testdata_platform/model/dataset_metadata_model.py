from pydantic import BaseModel, Field

from testdata_platform.model.config_model import ConfigModel
from testdata_platform.model.settings_model import SettingsModel


class DatasetMetadataModel(BaseModel):
    name: str
    config_file: str
    row_count: int
    column_count: int
    columns: list[str]
    destinations: list[str]
    file: str = Field(description="Path relative to the project root")
    download_url: str

    @classmethod
    def from_config(cls, config: ConfigModel, settings: SettingsModel) -> "DatasetMetadataModel":
        return cls(
            name=config.dataset_name,
            config_file=f"{settings.config_dir.name}/{config.name}",
            row_count=config.row_count,
            column_count=len(config.columns),
            columns=list(config.column_names),
            destinations=list(config.destinations),
            file=f"{config.output_dir.name}/{config.output_file('csv').name}",
            download_url=f"/datasets/{config.dataset_name}/download",
        )
