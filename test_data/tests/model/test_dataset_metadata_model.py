from pathlib import Path

from test_data.model.config_model import ConfigModel
from test_data.model.dataset_model import DatasetModel
from test_data.model.dataset_metadata_model import DatasetMetadataModel


def test_dataset_metadata_from_dataset(project_root: Path) -> None:
    metadata = DatasetMetadataModel.from_dataset(DatasetModel(name="demo", config=ConfigModel.from_file("demo.json")))

    assert metadata.name == "demo"
    assert metadata.config_file == "config/demo.json"
    assert metadata.file == "output_test/demo.csv"
    assert metadata.download_url == "/datasets/demo/download"
    assert metadata.row_count == 5
