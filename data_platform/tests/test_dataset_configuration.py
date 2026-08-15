from pathlib import Path

import pytest

from app_config import env_config as ec
from dataset.definition import (
    DatabaseConnection,
    Dataset,
    Destination,
    Datalake,
    DataWarehouse,
    FileSource,
    Source,
    StageDatabase,
    Streaming,
)
from dataset.house.config import HOUSE_DATASET
from dataset.registry import get_dataset, get_dataset_names
from dataset.sale.config import SALE_DATASET


class TestFileSource:

    def test_should_resolve_path_using_file_path_when_available(self) -> None:
        # Given
        given_source = FileSource(file_name="sale.csv", file_path=str(Path("C:/data/sale.csv")))

        # When
        actual = given_source.resolve_path("resources")

        # Then
        assert actual == Path("C:/data/sale.csv")

    def test_should_resolve_path_using_base_path_when_file_path_is_missing(self) -> None:
        # Given
        given_source = FileSource(file_name="sale.csv")

        # When
        actual = given_source.resolve_path(Path("resources"))

        # Then
        assert actual == Path("resources") / "sale.csv"


class TestDataset:

    def test_should_expose_grouped_configuration_through_compatibility_properties(self) -> None:
        # Given
        given_dataset = Dataset(
            name="example",
            dataframe_schema=None,
            required_columns=frozenset({"id"}),
            processors={},
            event_converter=lambda row: row,
            source=Source(
                file=FileSource(
                    file_name="example.csv",
                    file_path="/tmp/example.csv",
                )
            ),
            destination=Destination(
                datalake=Datalake(bucket_name="example-bucket"),
                database=StageDatabase(
                    connection=DatabaseConnection(server="localhost", port=5432, database_name="example"),
                    table_name="sale.example_stage",
                ),
                datawarehouse=DataWarehouse(
                    connection=DatabaseConnection(server="localhost", port=8123, database_name="warehouse"),
                    table_name="example_table",
                    full_table_name="app_datawarehouse.example_table",
                ),
            ),
            streaming=Streaming(
                server="kafka:9092",
                bootstrap_servers="kafka:9092",
                topic="example-events",
                consumer_group="example-consumer",
                checkpoint_path="/checkpoints/example",
                audit_topic="example-audit",
            ),
            event_key_column="id",
        )

        # Then
        assert given_dataset.file_name == "example.csv"
        assert given_dataset.file_path == "/tmp/example.csv"
        assert given_dataset.datalake.bucket_name == "example-bucket"
        assert given_dataset.database.table_name == "sale.example_stage"
        assert given_dataset.datawarehouse.full_table_name == "app_datawarehouse.example_table"
        assert given_dataset.streaming_topic == "example-events"
        assert given_dataset.streaming_consumer_group == "example-consumer"
        assert given_dataset.streaming_checkpoint_path == "/checkpoints/example"
        assert given_dataset.audit_topic == "example-audit"


class TestDatasetRegistry:

    def test_should_return_known_dataset_names(self) -> None:
        # When
        actual = get_dataset_names()

        # Then
        assert actual == ("house", "sale")

    def test_should_return_sale_dataset(self) -> None:
        # When
        actual = get_dataset("sale")

        # Then
        assert actual is SALE_DATASET

    def test_should_return_house_dataset(self) -> None:
        # When
        actual = get_dataset("house")

        # Then
        assert actual is HOUSE_DATASET

    def test_should_raise_error_for_unsupported_dataset(self) -> None:
        # When / Then
        with pytest.raises(ValueError):
            get_dataset("missing")


class TestConcreteDatasetConfiguration:

    def test_sale_dataset_should_include_streaming_server_and_source_path(self) -> None:
        # Then
        assert SALE_DATASET.streaming.server == ec.APP_STREAMING_BOOTSTRAP_SERVERS
        assert SALE_DATASET.streaming.bootstrap_servers == ec.APP_STREAMING_BOOTSTRAP_SERVERS
        assert SALE_DATASET.source.file.resolve_path(ec.RESOURCES_DIR).name == "sale.csv"
        assert SALE_DATASET.database.table_name == "sale.sale_stage"
        assert SALE_DATASET.datawarehouse.full_table_name == "app_datawarehouse.sale_table"

    def test_house_dataset_should_include_streaming_server_and_source_path(self) -> None:
        # Then
        assert HOUSE_DATASET.streaming.server == ec.APP_STREAMING_BOOTSTRAP_SERVERS
        assert HOUSE_DATASET.streaming.bootstrap_servers == ec.APP_STREAMING_BOOTSTRAP_SERVERS
        assert HOUSE_DATASET.source.file.resolve_path(ec.RESOURCES_DIR).name == "house.csv"
        assert HOUSE_DATASET.database.table_name == "house.house_stage"
        assert HOUSE_DATASET.datawarehouse.full_table_name == "app_datawarehouse.house_table"
