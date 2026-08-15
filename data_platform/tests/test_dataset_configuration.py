from pathlib import Path

import pytest

from config.app import settings as app_settings
from dataset.definition import (
    Audit,
    DataLakeEndpoint,
    DataWarehouseEndpoint,
    Dataframe,
    DatabaseEndpoint,
    Dataset,
    Event,
    FileEndpoint,
    MessagingEndpoint,
)
from dataset.house.config import HOUSE_DATASET
from dataset.registry import get_dataset, get_dataset_names
from dataset.sale.config import SALE_DATASET


class TestFileEndpoint:

    def test_should_resolve_path_using_file_path_when_available(self) -> None:
        given_endpoint = FileEndpoint(file_name="sale.csv", file_path=str(Path("C:/data/sale.csv")))

        actual = given_endpoint.resolve_path("resources")

        assert actual == Path("C:/data/sale.csv")

    def test_should_resolve_path_using_base_path_when_file_path_is_missing(self) -> None:
        given_endpoint = FileEndpoint(file_name="sale.csv")

        actual = given_endpoint.resolve_path(Path("resources"))

        assert actual == Path("resources") / "sale.csv"


class TestDataset:

    def test_should_lookup_sources_and_destinations(self) -> None:
        given_dataset = Dataset(
            name="example",
            dataframe=Dataframe(schema=None, required_columns=frozenset({"id"})),
            event=Event(key_column="id"),
            audit=Audit(topic="example-audit"),
            processor_factories={},
            sources={
                "file": FileEndpoint(file_name="example.csv", file_path="/tmp/example.csv"),
                "messaging": MessagingEndpoint(topic="example-events"),
            },
            destinations={
                "datalake": DataLakeEndpoint(bucket_name="example-bucket"),
                "database": DatabaseEndpoint(table_name="sale.example_stage"),
                "datawarehouse": DataWarehouseEndpoint(full_table_name="app_datawarehouse.example_table"),
            },
        )

        assert given_dataset.get_source("file").file_name == "example.csv"
        assert given_dataset.get_destination("datalake").bucket_name == "example-bucket"
        assert given_dataset.get_destination("database").table_name == "sale.example_stage"
        assert given_dataset.get_destination("datawarehouse").full_table_name == "app_datawarehouse.example_table"
        assert given_dataset.dataframe.schema is None
        assert given_dataset.dataframe.required_columns == frozenset({"id"})
        assert given_dataset.event.key_column == "id"
        assert not hasattr(given_dataset.event, "converter")
        assert given_dataset.audit.topic == "example-audit"

    def test_should_raise_error_for_missing_endpoint(self) -> None:
        given_dataset = Dataset(name="example")

        with pytest.raises(KeyError):
            given_dataset.get_source("missing")

        with pytest.raises(KeyError):
            given_dataset.get_destination("missing")


class TestDatasetRegistry:

    def test_should_return_known_dataset_names(self) -> None:
        actual = get_dataset_names()

        assert actual == ("house", "sale")

    def test_should_return_sale_dataset(self) -> None:
        assert get_dataset("sale") is SALE_DATASET

    def test_should_return_house_dataset(self) -> None:
        assert get_dataset("house") is HOUSE_DATASET

    def test_should_raise_error_for_unsupported_dataset(self) -> None:
        with pytest.raises(ValueError):
            get_dataset("missing")


class TestConcreteDatasetConfiguration:

    def test_sale_dataset_should_expose_logical_endpoints(self) -> None:
        assert SALE_DATASET.get_source("file").resolve_path(app_settings.resources_dir).name == "sale.csv"
        assert SALE_DATASET.get_source("messaging").topic == "sale-events"
        assert SALE_DATASET.get_destination("database").table_name == "sale.sale_stage"
        assert SALE_DATASET.get_destination("datawarehouse").full_table_name == "app_datawarehouse.sale_table"
        assert SALE_DATASET.audit.topic == "sale.audit.event.v1"

    def test_house_dataset_should_expose_logical_endpoints(self) -> None:
        assert HOUSE_DATASET.get_source("file").resolve_path(app_settings.resources_dir).name == "house.csv"
        assert HOUSE_DATASET.get_source("messaging").topic == "house-events"
        assert HOUSE_DATASET.get_destination("database").table_name == "house.house_stage"
        assert HOUSE_DATASET.get_destination("datawarehouse").full_table_name == "app_datawarehouse.house_table"
        assert HOUSE_DATASET.audit.topic == "sale.audit.event.v1"

    def test_dataset_processors_should_be_lazy(self) -> None:
        assert callable(SALE_DATASET.processor_factories["spark"])
        assert callable(HOUSE_DATASET.processor_factories["spark"])
