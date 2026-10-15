from testdata_platform.model.config_model import ConfigModel
from testdata_platform.model.dataset_metadata_model import DatasetMetadataModel
from testdata_platform.model.settings_model import SettingsModel


def test_dataset_metadata_from_config(settings: SettingsModel) -> None:
    metadata = DatasetMetadataModel.from_config(ConfigModel.from_file("demo.json", settings), settings)

    assert metadata.name == "demo"
    assert metadata.config_file == "config/demo.json"
    assert metadata.file == "output_test/demo.csv"
    assert metadata.download_url == "/datasets/demo/download"
    assert metadata.row_count == 5
