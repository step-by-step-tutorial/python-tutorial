from test_data.model.config_model import ConfigModel
from test_data.model.dataset_metadata_model import DatasetMetadataModel
from test_data.model.settings_model import SettingsModel


def test_dataset_metadata_from_config(settings: SettingsModel) -> None:
    metadata = DatasetMetadataModel.from_config(ConfigModel.from_file("demo.json", settings), settings)

    assert metadata.name == "demo"
    assert metadata.config_file == "config/demo.json"
    assert metadata.file == "output_test/demo.csv"
    assert metadata.download_url == "/datasets/demo/download"
    assert metadata.row_count == 5
