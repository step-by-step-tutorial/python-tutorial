from pathlib import Path

import pytest

from data_platform.model.endpoint_model import (
    AuditEndpointModel,
    DataLakeEndpointModel,
    WarehouseEndpointModel,
    DatabaseEndpointModel,
    FileEndpointModel,
    MessagingEndpointModel,
    RestApiEndpointModel,
)
from data_platform.model.dataframe_model import DataFrameModel
from data_platform.model.dataset_model import DatasetModel
from data_platform.config.key import Key
from data_platform.config.pipeline_type import PipelineType
from data_platform.registry.bootstrap import initialize_registries
from data_platform.registry.dataset_registry import dataset_registry
from data_platform.registry.endpoint_registry import endpoint_registry

initialize_registries()
house_dataset = dataset_registry.create_dataset("house", PipelineType.INMEMORY)
ONLINE_SHOPPING_DATASET = dataset_registry.create_dataset("online_shopping", PipelineType.INMEMORY)


class TestDataset:

    def test_should_lookup_sources_and_destinations(self) -> None:
        given_dataset = DatasetModel(
            name="example",
            dataframe=DataFrameModel(schema=None, required_columns=frozenset({"id"})),
            audit=AuditEndpointModel(
                database_connection_name="audit.database",
                messaging_connection_name="audit.kafka.producer",
                datalake_connection_name="audit.datalake",
                create_sql_files={"create": "database/audit/create_tables.sql"},
                channel_name="example-audit",
                bucket_name="example-audit-bucket",
                write_sql_files={"write": "database/audit/insert_event.sql"},
            ),
            endpoints={
                "example.file.csv": FileEndpointModel(file_name="example.csv", file_path="/tmp/example.csv"),
                "example.kafka.listener": MessagingEndpointModel(connection_name="example.kafka.listener",
                                                         channel_name="example-events"),
                "example.datalake": DataLakeEndpointModel(connection_name="example.datalake", bucket_name="example-bucket"),
                "example.database": DatabaseEndpointModel(
                    connection_name="example.database",
                    schema="example",
                    stage_table_name="example_stage",
                ),
                "example.warehouse": WarehouseEndpointModel(
                    connection_name="example.warehouse",
                    schema="app_warehouse",
                    table_name="example_table",
                ),
            },
        )

        assert given_dataset.get_endpoint("example.file.csv", FileEndpointModel).file_name == "example.csv"
        assert given_dataset.get_endpoint("example.datalake", DataLakeEndpointModel).bucket_name == "example-bucket"
        assert given_dataset.get_endpoint("example.database", DatabaseEndpointModel).schema == "example"
        assert given_dataset.get_endpoint("example.database", DatabaseEndpointModel).stage_table_name == "example_stage"
        assert given_dataset.get_endpoint("example.database",
                                          DatabaseEndpointModel).full_stage_table_name == "example.example_stage"
        assert given_dataset.get_endpoint("example.warehouse",
                                          WarehouseEndpointModel).full_table_name == "app_warehouse.example_table"
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

        with pytest.raises(TypeError, match="not a DatabaseEndpointModel"):
            given_dataset.get_endpoint("example.file.csv", DatabaseEndpointModel)

    def test_should_raise_error_for_missing_endpoint(self) -> None:
        given_dataset = DatasetModel(name="example", audit=endpoint_registry.get_item(Key.AUDIT))

        with pytest.raises(KeyError):
            given_dataset.get_endpoint("missing", FileEndpointModel)

        with pytest.raises(KeyError):
            given_dataset.get_endpoint("missing", DatabaseEndpointModel)


class TestDatasetRegistry:
    def test_should_create_a_fresh_dataset_per_pipeline_type(self) -> None:
        first = dataset_registry.create_dataset("house", PipelineType.INMEMORY)
        second = dataset_registry.create_dataset("house", PipelineType.INMEMORY)

        assert first.name == "house"
        assert first is not second

    def test_should_raise_error_for_unsupported_dataset(self) -> None:
        with pytest.raises(ValueError):
            dataset_registry.get_item("missing")


class TestConcreteDatasetConfiguration:

    @pytest.mark.parametrize("dataset, storage_object_name", [
        (house_dataset, "api"),
        (ONLINE_SHOPPING_DATASET, "api"),
    ])
    def test_each_dataset_declares_the_complete_pipeline_stages(self, dataset, storage_object_name) -> None:
        definition = dataset.flow
        assert definition is not None
        assert [stage.name for stage in definition.ingestors] == [storage_object_name]
        assert definition.cleaners
        assert definition.validators
        assert definition.enrichers is not None
        assert definition.exposers
        assert definition.analyzers

    def test_house_dataset_should_expose_logical_endpoints(self) -> None:
        for endpoint_name, endpoint in house_dataset.endpoints.items():
            assert endpoint.name == endpoint_name

        assert Path(house_dataset.get_endpoint("house.file.csv", FileEndpointModel).file_path).name == "house.csv"
        house_api = house_dataset.get_endpoint("house.rest.api", RestApiEndpointModel)
        assert house_api.url.endswith("/datasets/house/download?format=csv")
        assert house_dataset.get_endpoint("house.kafka.listener", MessagingEndpointModel).channel_name == "house.events.v1"
        assert house_dataset.get_endpoint("house.kafka.listener",
                                          MessagingEndpointModel).connection_name == "house.kafka.listener"
        assert house_dataset.get_endpoint("house.database", DatabaseEndpointModel).schema == "house"
        assert house_dataset.get_endpoint("house.database", DatabaseEndpointModel).stage_table_name == "house_stage"
        assert house_dataset.get_endpoint("house.database",
                                          DatabaseEndpointModel).full_stage_table_name == "house.house_stage"
        assert house_dataset.get_endpoint("house.database", DatabaseEndpointModel).connection_name == "house.database"
        assert house_dataset.get_endpoint("house.datalake", DataLakeEndpointModel).connection_name == "house.datalake"
        assert house_dataset.get_endpoint("house.warehouse", WarehouseEndpointModel).schema == "app_warehouse"
        assert house_dataset.get_endpoint("house.warehouse",
                                          WarehouseEndpointModel).connection_name == "house.warehouse"
        assert house_dataset.get_endpoint("house.warehouse",
                                          WarehouseEndpointModel).full_table_name == "app_warehouse.house_table"
        assert house_dataset.audit.database_connection_name == "audit.database"
        assert house_dataset.audit.messaging_connection_name == "audit.kafka.producer"
        assert house_dataset.audit.datalake_connection_name == "audit.datalake"
        assert house_dataset.audit.create_sql_files == {"create": "database/audit/create_tables.sql"}
        assert house_dataset.audit.channel_name == "audit.audit.events.v1"
        assert house_dataset.audit.write_sql_files == {"write": "database/audit/insert_event.sql"}

    def test_pipeline_steps_is_the_only_pipeline_stage_configuration(self) -> None:
        for dataset in (house_dataset, ONLINE_SHOPPING_DATASET):
            assert not hasattr(dataset, "transformers")
            assert not hasattr(dataset, "analyzers")
            assert not hasattr(dataset, "get_transformer")
            assert not hasattr(dataset, "get_analyzer")
            assert dataset.flow is not None

    def test_online_shopping_should_use_the_complete_standard_flow(self) -> None:
        definition = ONLINE_SHOPPING_DATASET.flow
        assert definition is not None
        assert [stage.name for stage in definition.ingestors] == ["api"]
        assert definition.cleaners
        assert definition.validators
        assert definition.enrichers
        assert definition.exposers
        assert definition.analyzers
