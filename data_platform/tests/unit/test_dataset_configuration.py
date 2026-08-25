from pathlib import Path

import pytest

from data_platform.model import (
    AuditEndpoint,
    DataLakeEndpoint,
    WarehouseEndpoint,
    DataFrameModel,
    DatabaseEndpoint,
    Dataset,
    FileEndpoint,
    MessagingEndpoint,
    RestApiEndpoint,
)
from data_platform.registry.dataset_registry import dataset_registry
from data_platform.registry.bootstrap import initialize_registries
from data_platform.registry.endpoint_registry import endpoint_registry
from data_platform.config.main_settings import settings
initialize_registries()

from data_platform.domain.house.dataset import house_dataset
from data_platform.domain.sale.dataset import sale_dataset
from data_platform.domain.online_shopping.dataset import ONLINE_SHOPPING_DATASET


class TestDataset:

    def test_should_lookup_sources_and_destinations(self) -> None:
        given_dataset = Dataset(
            name="example",
            dataframe=DataFrameModel(schema=None, required_columns=frozenset({"id"})),
            audit=AuditEndpoint(
                database_connection_name="audit.database",
                messaging_connection_name="audit.kafka.producer",
                datalake_connection_name="audit.datalake",
                create_sql_files={"create": "database/audit/create_tables.sql"},
                channel_name="example-audit",
                bucket_name="example-audit-bucket",
                write_sql_files={"write": "database/audit/insert_event.sql"},
            ),
            endpoints={
                "sale.file.csv": FileEndpoint(file_name="sale.csv", file_path="/tmp/example.csv"),
                "sale.kafka.listener": MessagingEndpoint(connection_name="sale.kafka.listener",
                                                         channel_name="example-events"),
                "sale.datalake": DataLakeEndpoint(connection_name="sale.datalake", bucket_name="example-bucket"),
                "sale.database": DatabaseEndpoint(
                    connection_name="sale.database",
                    schema="sale",
                    stage_table_name="example_stage",
                    full_stage_table_name="sale.example_stage",
                    table_names=["sale.example_stage"],
                ),
                "sale.warehouse": WarehouseEndpoint(
                    connection_name="sale.warehouse",
                    schema="app_warehouse",
                    table_name="example_table",
                    full_table_name="app_warehouse.example_table",
                ),
            },
        )

        assert given_dataset.get_endpoint("sale.file.csv", FileEndpoint).file_name == "sale.csv"
        assert given_dataset.get_endpoint("sale.datalake", DataLakeEndpoint).bucket_name == "example-bucket"
        assert given_dataset.get_endpoint("sale.database", DatabaseEndpoint).schema == "sale"
        assert given_dataset.get_endpoint("sale.database", DatabaseEndpoint).stage_table_name == "example_stage"
        assert given_dataset.get_endpoint("sale.database",
                                          DatabaseEndpoint).full_stage_table_name == "sale.example_stage"
        assert given_dataset.get_endpoint("sale.database", DatabaseEndpoint).table_names == ["sale.example_stage"]
        assert given_dataset.get_endpoint("sale.warehouse",
                                          WarehouseEndpoint).full_table_name == "app_warehouse.example_table"
        assert given_dataset.dataframe.schema is None
        assert given_dataset.dataframe.required_columns == frozenset({"id"})
        assert given_dataset.audit.database_connection_name == "audit.database"
        assert given_dataset.audit.messaging_connection_name == "audit.kafka.producer"
        assert given_dataset.audit.datalake_connection_name == "audit.datalake"
        assert given_dataset.audit.channel_name == "example-audit"
        assert given_dataset.audit.bucket_name == "example-audit-bucket"
        assert given_dataset.audit.create_sql_files == {"create": "database/audit/create_tables.sql"}
        assert given_dataset.audit.write_sql_files == {"write": "database/audit/insert_event.sql"}
        assert not hasattr(given_dataset, "event")

        with pytest.raises(TypeError, match="not a DatabaseEndpoint"):
            given_dataset.get_endpoint("sale.file.csv", DatabaseEndpoint)

    def test_should_raise_error_for_missing_endpoint(self) -> None:
        given_dataset = Dataset(name="example", audit=endpoint_registry.get_item("audit"))

        with pytest.raises(KeyError):
            given_dataset.get_endpoint("missing", FileEndpoint)

        with pytest.raises(KeyError):
            given_dataset.get_endpoint("missing", DatabaseEndpoint)


class TestDatasetRegistry:
    def test_should_return_sale_dataset(self) -> None:
        assert dataset_registry.get_item("sale") is sale_dataset

    def test_should_return_house_dataset(self) -> None:
        assert dataset_registry.get_item("house") is house_dataset

    def test_should_raise_error_for_unsupported_dataset(self) -> None:
        with pytest.raises(ValueError):
            dataset_registry.get_item("missing")


class TestConcreteDatasetConfiguration:

    @pytest.mark.parametrize("dataset, storage_object_name", [
        (sale_dataset, "csv"),
        (house_dataset, "csv"),
        (ONLINE_SHOPPING_DATASET, "api"),
    ])
    def test_each_dataset_declares_the_complete_pipeline_stages(self, dataset, storage_object_name) -> None:
        definition = dataset.flow
        assert definition is not None
        assert [stage.pipeline_name for stage in definition.ingestors] == [storage_object_name]
        assert definition.cleaners
        assert definition.validators
        assert definition.enrichers
        assert definition.exposers
        assert definition.analyzers

    def test_sale_dataset_should_expose_logical_endpoints(self) -> None:
        for endpoint_name, endpoint in sale_dataset.endpoints.items():
            assert endpoint.pipeline_name == endpoint_name

        assert Path(sale_dataset.get_endpoint("sale.file.csv", FileEndpoint).file_path).name == "sale.csv"
        assert sale_dataset.get_endpoint("sale.kafka.listener", MessagingEndpoint).channel_name == "sale-events"
        assert sale_dataset.get_endpoint("sale.kafka.listener",
                                         MessagingEndpoint).connection_name == "sale.kafka.listener"
        assert sale_dataset.get_endpoint("sale.database", DatabaseEndpoint).schema == "sale"
        assert sale_dataset.get_endpoint("sale.database", DatabaseEndpoint).stage_table_name == "sale_stage"
        assert sale_dataset.get_endpoint("sale.database", DatabaseEndpoint).full_stage_table_name == "sale.sale_stage"
        assert sale_dataset.get_endpoint("sale.database", DatabaseEndpoint).table_names == [
            "sale.sale_stage",
            "sale.customer",
            "sale.product",
            "sale.order",
            "sale.order_item",
        ]
        assert sale_dataset.get_endpoint("sale.database", DatabaseEndpoint).connection_name == "sale.database"
        assert sale_dataset.get_endpoint("sale.datalake", DataLakeEndpoint).connection_name == "sale.datalake"
        assert sale_dataset.get_endpoint("sale.warehouse", WarehouseEndpoint).schema == "app_warehouse"
        assert sale_dataset.get_endpoint("sale.warehouse",
                                         WarehouseEndpoint).connection_name == "sale.warehouse"
        assert sale_dataset.get_endpoint("sale.warehouse",
                                         WarehouseEndpoint).full_table_name == "app_warehouse.sale_table"
        assert sale_dataset.get_endpoint("sale.rest", RestApiEndpoint).url.endswith("/datasets/sale.json/download?format=json")
        assert sale_dataset.get_endpoint("sale.rest", RestApiEndpoint).method == "GET"
        assert sale_dataset.audit.database_connection_name == "audit.database"
        assert sale_dataset.audit.messaging_connection_name == "audit.kafka.producer"
        assert sale_dataset.audit.datalake_connection_name == "audit.datalake"
        assert sale_dataset.audit.create_sql_files == {"create": "database/audit/create_tables.sql"}
        assert sale_dataset.audit.channel_name == "sale.audit.event.v1"
        assert sale_dataset.audit.write_sql_files == {"write": "database/audit/insert_event.sql"}

    def test_house_dataset_should_expose_logical_endpoints(self) -> None:
        for endpoint_name, endpoint in house_dataset.endpoints.items():
            assert endpoint.pipeline_name == endpoint_name

        assert Path(house_dataset.get_endpoint("house.file.csv", FileEndpoint).file_path).name == "house.csv"
        assert house_dataset.get_endpoint("house.kafka.listener", MessagingEndpoint).channel_name == "house-events"
        assert house_dataset.get_endpoint("house.kafka.listener",
                                          MessagingEndpoint).connection_name == "house.kafka.listener"
        assert house_dataset.get_endpoint("house.database", DatabaseEndpoint).schema == "house"
        assert house_dataset.get_endpoint("house.database", DatabaseEndpoint).stage_table_name == "house_stage"
        assert house_dataset.get_endpoint("house.database",
                                          DatabaseEndpoint).full_stage_table_name == "house.house_stage"
        assert house_dataset.get_endpoint("house.database", DatabaseEndpoint).table_names == ["house.house_stage"]
        assert house_dataset.get_endpoint("house.database", DatabaseEndpoint).connection_name == "house.database"
        assert house_dataset.get_endpoint("house.datalake", DataLakeEndpoint).connection_name == "house.datalake"
        assert house_dataset.get_endpoint("house.warehouse", WarehouseEndpoint).schema == "app_warehouse"
        assert house_dataset.get_endpoint("house.warehouse",
                                          WarehouseEndpoint).connection_name == "house.warehouse"
        assert house_dataset.get_endpoint("house.warehouse",
                                          WarehouseEndpoint).full_table_name == "app_warehouse.house_table"
        assert house_dataset.audit.database_connection_name == "audit.database"
        assert house_dataset.audit.messaging_connection_name == "audit.kafka.producer"
        assert house_dataset.audit.datalake_connection_name == "audit.datalake"
        assert house_dataset.audit.create_sql_files == {"create": "database/audit/create_tables.sql"}
        assert house_dataset.audit.channel_name == "sale.audit.event.v1"
        assert house_dataset.audit.write_sql_files == {"write": "database/audit/insert_event.sql"}

    def test_pipeline_steps_is_the_only_pipeline_stage_configuration(self) -> None:
        for dataset in (sale_dataset, house_dataset, ONLINE_SHOPPING_DATASET):
            assert not hasattr(dataset, "transformers")
            assert not hasattr(dataset, "analyzers")
            assert not hasattr(dataset, "get_transformer")
            assert not hasattr(dataset, "get_analyzer")
            assert dataset.flow is not None

    def test_online_shopping_should_use_the_complete_standard_flow(self) -> None:
        definition = ONLINE_SHOPPING_DATASET.flow
        assert definition is not None
        assert [stage.pipeline_name for stage in definition.ingestors] == ["api"]
        assert definition.cleaners
        assert definition.validators
        assert definition.enrichers
        assert definition.exposers
        assert definition.analyzers
