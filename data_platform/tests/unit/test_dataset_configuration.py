from pathlib import Path

import pytest

from data_platform.model import (
    AuditEndpoint,
    DataLakeEndpoint,
    DataWarehouseEndpoint,
    DataFrameDefinition,
    DatabaseEndpoint,
    Dataset,
    FileEndpoint,
    MessagingEndpoint,
    RestApiEndpoint,
)
from data_platform.dataset.house_config import HOUSE_DATASET
from data_platform.dataset.registry import get_dataset
from data_platform.dataset.shared_endpoints import AUDIT_ENDPOINT
from data_platform.config.main_settings import settings
from data_platform.dataset.sale_config import SALE_DATASET


class TestDataset:

    def test_should_lookup_sources_and_destinations(self) -> None:
        given_dataset = Dataset(
            name="example",
            dataframe=DataFrameDefinition(schema=None, required_columns=frozenset({"id"})),
            audit=AuditEndpoint(
                database_connection_name="audit.database",
                messaging_connection_name="audit.kafka.producer",
                datalake_connection_name="audit.datalake",
                create_sql_files={"create": "database/audit/create_tables.sql"},
                channel_name="example-audit",
                bucket_name="example-audit-bucket",
                write_sql_files={"write": "database/audit/insert_event.sql"},
            ),
            processors={},
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
                "sale.datawarehouse": DataWarehouseEndpoint(
                    connection_name="sale.datawarehouse",
                    schema="app_datawarehouse",
                    table_name="example_table",
                    full_table_name="app_datawarehouse.example_table",
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
        assert given_dataset.get_endpoint("sale.datawarehouse",
                                          DataWarehouseEndpoint).full_table_name == "app_datawarehouse.example_table"
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
        given_dataset = Dataset(name="example", audit=AUDIT_ENDPOINT)

        with pytest.raises(KeyError):
            given_dataset.get_endpoint("missing", FileEndpoint)

        with pytest.raises(KeyError):
            given_dataset.get_endpoint("missing", DatabaseEndpoint)


class TestDatasetRegistry:
    def test_should_return_sale_dataset(self) -> None:
        assert get_dataset("sale") is SALE_DATASET

    def test_should_return_house_dataset(self) -> None:
        assert get_dataset("house") is HOUSE_DATASET

    def test_should_raise_error_for_unsupported_dataset(self) -> None:
        with pytest.raises(ValueError):
            get_dataset("missing")


class TestConcreteDatasetConfiguration:

    def test_sale_dataset_should_expose_logical_endpoints(self) -> None:
        for endpoint_name, endpoint in SALE_DATASET.endpoints.items():
            assert endpoint.name == endpoint_name

        assert Path(SALE_DATASET.get_endpoint("sale.file.csv", FileEndpoint).file_path).name == "sale.csv"
        assert SALE_DATASET.get_endpoint("sale.kafka.listener", MessagingEndpoint).channel_name == "sale-events"
        assert SALE_DATASET.get_endpoint("sale.kafka.listener",
                                         MessagingEndpoint).connection_name == "sale.kafka.listener"
        assert SALE_DATASET.get_endpoint("sale.database", DatabaseEndpoint).schema == "sale"
        assert SALE_DATASET.get_endpoint("sale.database", DatabaseEndpoint).stage_table_name == "sale_stage"
        assert SALE_DATASET.get_endpoint("sale.database", DatabaseEndpoint).full_stage_table_name == "sale.sale_stage"
        assert SALE_DATASET.get_endpoint("sale.database", DatabaseEndpoint).table_names == [
            "sale.sale_stage",
            "sale.customer",
            "sale.product",
            "sale.order",
            "sale.order_item",
        ]
        assert SALE_DATASET.get_endpoint("sale.database", DatabaseEndpoint).connection_name == "sale.database"
        assert SALE_DATASET.get_endpoint("sale.datalake", DataLakeEndpoint).connection_name == "sale.datalake"
        assert SALE_DATASET.get_endpoint("sale.datawarehouse", DataWarehouseEndpoint).schema == "app_datawarehouse"
        assert SALE_DATASET.get_endpoint("sale.datawarehouse",
                                         DataWarehouseEndpoint).connection_name == "sale.datawarehouse"
        assert SALE_DATASET.get_endpoint("sale.datawarehouse",
                                         DataWarehouseEndpoint).full_table_name == "app_datawarehouse.sale_table"
        assert SALE_DATASET.get_endpoint("sale.rest", RestApiEndpoint).url == settings.test_data.download_url
        assert SALE_DATASET.get_endpoint("sale.rest", RestApiEndpoint).method == "GET"
        assert SALE_DATASET.audit.database_connection_name == "audit.database"
        assert SALE_DATASET.audit.messaging_connection_name == "audit.kafka.producer"
        assert SALE_DATASET.audit.datalake_connection_name == "audit.datalake"
        assert SALE_DATASET.audit.create_sql_files == {"create": "database/audit/create_tables.sql"}
        assert SALE_DATASET.audit.channel_name == "sale.audit.event.v1"
        assert SALE_DATASET.audit.write_sql_files == {"write": "database/audit/insert_event.sql"}

    def test_house_dataset_should_expose_logical_endpoints(self) -> None:
        for endpoint_name, endpoint in HOUSE_DATASET.endpoints.items():
            assert endpoint.name == endpoint_name

        assert Path(HOUSE_DATASET.get_endpoint("house.file.csv", FileEndpoint).file_path).name == "house.csv"
        assert HOUSE_DATASET.get_endpoint("house.kafka.listener", MessagingEndpoint).channel_name == "house-events"
        assert HOUSE_DATASET.get_endpoint("house.kafka.listener",
                                          MessagingEndpoint).connection_name == "house.kafka.listener"
        assert HOUSE_DATASET.get_endpoint("house.database", DatabaseEndpoint).schema == "house"
        assert HOUSE_DATASET.get_endpoint("house.database", DatabaseEndpoint).stage_table_name == "house_stage"
        assert HOUSE_DATASET.get_endpoint("house.database",
                                          DatabaseEndpoint).full_stage_table_name == "house.house_stage"
        assert HOUSE_DATASET.get_endpoint("house.database", DatabaseEndpoint).table_names == ["house.house_stage"]
        assert HOUSE_DATASET.get_endpoint("house.database", DatabaseEndpoint).connection_name == "house.database"
        assert HOUSE_DATASET.get_endpoint("house.datalake", DataLakeEndpoint).connection_name == "house.datalake"
        assert HOUSE_DATASET.get_endpoint("house.datawarehouse", DataWarehouseEndpoint).schema == "app_datawarehouse"
        assert HOUSE_DATASET.get_endpoint("house.datawarehouse",
                                          DataWarehouseEndpoint).connection_name == "house.datawarehouse"
        assert HOUSE_DATASET.get_endpoint("house.datawarehouse",
                                          DataWarehouseEndpoint).full_table_name == "app_datawarehouse.house_table"
        assert HOUSE_DATASET.audit.database_connection_name == "audit.database"
        assert HOUSE_DATASET.audit.messaging_connection_name == "audit.kafka.producer"
        assert HOUSE_DATASET.audit.datalake_connection_name == "audit.datalake"
        assert HOUSE_DATASET.audit.create_sql_files == {"create": "database/audit/create_tables.sql"}
        assert HOUSE_DATASET.audit.channel_name == "sale.audit.event.v1"
        assert HOUSE_DATASET.audit.write_sql_files == {"write": "database/audit/insert_event.sql"}

    def test_dataset_processors_should_be_lazy(self) -> None:
        assert SALE_DATASET.processors["spark"] is not None
        assert HOUSE_DATASET.processors["spark"] is not None
