import pandas as pd

from pyspark.sql import SparkSession

from data_platform.model.endpoints import (
    DataLakeEndpoint,
    WarehouseEndpoint,
    DatabaseEndpoint,
    FileEndpoint,
    MessagingEndpoint,
    RestApiEndpoint,
)
from data_platform.ingestion.csv_file_ingestor import CsvFileIngestor
from data_platform.ingestion.database_ingestor import DatabaseIngestor
from data_platform.ingestion.data_lake_ingestor import DataLakeIngestor
from data_platform.ingestion.warehouse_ingestor import WarehouseIngestor
from data_platform.ingestion.kafka_ingestor import KafkaIngestor
from data_platform.ingestion.rest_api_ingestor import RestApiIngestor
from data_platform.ingestion.spark_kafka_ingestor import SparkKafkaIngestor
from data_platform.ingestion.spark_csv_file_ingestor import SparkCsvFileIngestor


class TestCsvFileIngestor:

    def test_should_read_csv_file(self, tmp_path) -> None:
        csv_path = tmp_path / "sample.csv"
        expected = pd.DataFrame({"id": [1], "name": ["Alice"]})
        expected.to_csv(csv_path, index=False)

        ingestor = CsvFileIngestor(endpoint=FileEndpoint(file_path=str(csv_path)))

        actual = ingestor.ingest()

        pd.testing.assert_frame_equal(actual, expected)


class TestSparkCsvFileIngestor:

    def test_should_delegate_to_spark_reader(self, mocker) -> None:
        given_spark = mocker.MagicMock(spec=SparkSession)
        given_dataframe = mocker.Mock()
        given_spark.read.option.return_value.schema.return_value.csv.return_value = given_dataframe
        ingestor = SparkCsvFileIngestor(session=given_spark)

        actual = ingestor.ingest(file_path="/tmp/sample.csv", schema={"schema": "value"})

        assert actual is given_dataframe
        assert given_spark.read.option.call_count == 1
        assert given_spark.read.option.call_args.args == ("header", "true")
        assert given_spark.read.option.return_value.schema.call_count == 1
        assert given_spark.read.option.return_value.schema.call_args.args[0] == {"schema": "value"}
        assert given_spark.read.option.return_value.schema.return_value.csv.call_count == 1
        assert given_spark.read.option.return_value.schema.return_value.csv.call_args.args[0].endswith("sample.csv")


class TestDataLakeIngestor:

    def test_should_delegate_to_datalake_service(self, mocker) -> None:
        given_dataframe = pd.DataFrame({"id": [1]})
        given_client = mocker.Mock()
        given_client.list_objects_v2.return_value = {"Contents": [{"Key": "raw/part-001.parquet"}]}
        given_client.download_fileobj.side_effect = lambda bucket, key, buffer: buffer.write(b"parquet")
        mocker.patch("data_platform.repository.inmemory_datalake_repository.connection_registry.get_item", return_value=given_client)
        mocker.patch("data_platform.ingestion.data_lake_ingestor.pd.read_parquet", return_value=given_dataframe)
        mocker.patch("data_platform.ingestion.data_lake_ingestor.pd.concat", return_value=given_dataframe)

        actual = DataLakeIngestor(
            endpoint=DataLakeEndpoint(
                connection_name="house.datalake",
                bucket_name="bucket",
            )
        ).ingest("raw/example")

        assert actual is given_dataframe
        assert given_client.list_objects_v2.call_count == 1


class TestRestApiIngestor:

    def test_should_normalize_json_payload(self, mocker) -> None:
        given_response = mocker.Mock()
        given_response.__enter__ = mocker.Mock(return_value=given_response)
        given_response.__exit__ = mocker.Mock(return_value=None)
        given_response.read.return_value = b'[{"id": 1}, {"id": 2}]'
        given_connection = mocker.Mock()
        given_connection.open.return_value = given_response
        mock_build_opener = mocker.patch("data_platform.ingestion.rest_api_ingestor.build_opener", return_value=given_connection)

        actual = RestApiIngestor(
            endpoint=RestApiEndpoint(
                url="https://example.test/data",
                method="GET",
            )
        ).ingest()

        assert list(actual["id"]) == [1, 2]
        assert mock_build_opener.call_count == 1
        assert given_connection.open.call_count == 1


class TestMessageQueueIngestor:

    def test_should_collect_json_messages(self, mocker) -> None:
        given_consumer = mocker.Mock()
        given_message_1 = mocker.Mock()
        given_message_1.error.return_value = None
        given_message_1.value.return_value = b'{"id": 1}'
        given_message_2 = mocker.Mock()
        given_message_2.error.return_value = None
        given_message_2.value.return_value = b'{"id": 2}'
        given_consumer.poll.side_effect = [given_message_1, given_message_2, None]
        mocker.patch("data_platform.ingestion.kafka_ingestor.connection_registry.get_item", return_value=given_consumer)

        actual = KafkaIngestor(
            endpoint=MessagingEndpoint(
                connection_name="house.kafka.listener",
                channel_name="queue",
                timeout_ms=1000,
                max_messages=1000,
            )
        ).ingest()

        assert list(actual["id"]) == [1, 2]
        assert given_consumer.subscribe.call_count == 1
        assert given_consumer.close.call_count == 1


class TestDatabaseIngestor:

    def test_should_read_table_via_sql_connection(self, mocker) -> None:
        given_dataset = DatabaseEndpoint(
            connection_name="house.database",
            schema="house",
            stage_table_name="example_stage",
            full_stage_table_name="house.example_stage",
            table_names=["house.example_stage"],
            query_sql_files={"select_all": "database/select_all.sql"},
        )
        given_engine = mocker.Mock()
        given_connection = mocker.Mock()
        given_context = mocker.MagicMock()
        given_context.__enter__.return_value = given_connection
        given_engine.connect.return_value = given_context
        mocker.patch("data_platform.ingestion.database_ingestor.read_text_file", return_value="select * from {table_name}")
        expected = pd.DataFrame({"id": [1]})
        mock_execute = mocker.patch("data_platform.ingestion.database_ingestor.execute_query_strings", return_value=expected)

        actual = DatabaseIngestor(endpoint=given_dataset).ingest(given_dataset.full_stage_table_name)

        assert actual is expected
        assert mock_execute.call_count == 1
        assert mock_execute.call_args.args[0] == "house.database"
        assert mock_execute.call_args.args[1] == ("select * from house.example_stage",)


class TestWarehouseIngestor:

    def test_should_query_full_table(self, mocker) -> None:
        given_endpoint = WarehouseEndpoint(
            connection_name="house.warehouse",
            schema="warehouse",
            table_name="example",
            full_table_name="warehouse.example",
            query_sql_files={"select_all": "warehouse/select_all.sql"},
        )
        given_connection = mocker.Mock()
        mocker.patch("data_platform.ingestion.warehouse_ingestor.connection_registry.get_item", return_value=given_connection)
        mocker.patch("data_platform.ingestion.warehouse_ingestor.read_text_file", return_value="select * from {table_name}")
        expected = pd.DataFrame({"id": [1]})
        given_connection.query_df.return_value = expected

        actual = WarehouseIngestor(endpoint=given_endpoint).ingest(given_endpoint.full_table_name)

        assert actual is expected
        assert given_connection.query_df.call_count == 1
        assert given_connection.query_df.call_args.args[0] == "select * from warehouse.example"


class TestStreamingChannelIngestor:

    def test_should_read_stream_from_topic(self, mocker) -> None:
        given_spark = mocker.Mock()
        given_dataframe = mocker.Mock()
        given_stream_reader = given_spark.read.format.return_value
        given_option_one = given_stream_reader.option.return_value
        given_option_two = given_option_one.option.return_value
        given_option_three = given_option_two.option.return_value
        given_option_four = given_option_three.option.return_value
        given_option_five = given_option_four.option.return_value
        given_option_five.load.return_value = given_dataframe
        given_dataframe.select.return_value = given_dataframe
        given_column = mocker.Mock()
        given_column.cast.return_value = "value-as-string"
        mock_col = mocker.patch("data_platform.ingestion.spark_kafka_ingestor.sf.col", return_value=given_column)
        mock_from_json = mocker.patch("data_platform.ingestion.spark_kafka_ingestor.sf.from_json")
        mock_from_json.return_value.alias.return_value = "payload"

        ingestor = SparkKafkaIngestor(
            endpoint=MessagingEndpoint(
                connection_name="house.kafka.listener",
                channel_name="example-events",
                bootstrap_servers="localhost:9092",
                starting_offsets="earliest",
            ),
            session=given_spark,
            schema={"schema": "value"},
        )

        actual = ingestor.ingest()

        assert actual is given_dataframe
        assert mock_col.call_count == 1
        assert mock_from_json.call_count == 1
        assert given_spark.read.format.call_count == 1
        assert given_stream_reader.option.call_count == 1
        assert given_option_one.option.call_count == 1
        assert given_option_two.option.call_count == 1
        assert given_option_three.option.call_count == 1
        assert given_option_five.load.call_count == 1
        assert given_dataframe.select.call_count == 2


