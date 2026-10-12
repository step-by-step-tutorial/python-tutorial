from pydantic import BaseModel, Field

from test_data.config import settings as env_config
from test_data.model.dataset_model import DatasetModel


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
    def from_dataset(cls, dataset: DatasetModel) -> "DatasetMetadataModel":
        return cls(
            name=dataset.name,
            config_file=f"{env_config.CONFIG_DIR.name}/{dataset.config.name}",
            row_count=dataset.config.row_count,
            column_count=len(dataset.columns),
            columns=list(dataset.columns),
            destinations=list(dataset.destinations),
            file=f"{env_config.OUTPUT_DIR.name}/{dataset.output_file.name}",
            download_url=f"/datasets/{dataset.name}/download",
        )
