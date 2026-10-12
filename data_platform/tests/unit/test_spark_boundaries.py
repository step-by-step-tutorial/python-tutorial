import pytest

pytest.importorskip("pyspark")

from data_platform.connector import spark_connector  # noqa: E402
from data_platform.model.endpoint_model import DataLakeEndpointModel  # noqa: E402
from data_platform.ingestion.spark_datalake_ingestor import SparkDatalakeIngestor  # noqa: E402
from data_platform.repository.spark_database_repository import SparkDatabaseRepository  # noqa: E402
from data_platform.repository.spark_datalake_repository import SparkDatalakeRepository  # noqa: E402


def test_spark_connector_reuses_active_session(mocker) -> None:
    active_session = mocker.Mock()
    mocker.patch.object(spark_connector.SparkSession, "getActiveSession", return_value=active_session)
    mocker.patch.object(spark_connector, "_is_session_active", return_value=True)

    assert spark_connector.create_session() is active_session


def test_spark_connector_detects_stopped_or_invalid_sessions(mocker) -> None:
    stopped = mocker.Mock()
    stopped.sparkContext._jsc.sc.return_value.isStopped.return_value = True
    assert spark_connector._is_session_active(stopped) is False
    assert spark_connector._is_session_active(object()) is False


def test_spark_database_repository_writes_to_stage_table(mocker) -> None:
    class Writer:
        saved = False

        def format(self, value):
            return self

        def option(self, name, value):
            return self

        def mode(self, value):
            return self

        def save(self):
            self.saved = True

    spark_dataframe = mocker.Mock()
    writer = Writer()
    spark_dataframe.write = writer
    spark_repository = SparkDatabaseRepository(type("Endpoint", (), {
        "connection_name": "house.database",
        "truncate_sql_files": {},
        "write_sql_files": {},
        "full_stage_table_name": "house.house_stage",
    })())
    spark_repository.write(spark_dataframe)
    assert writer.saved


def test_spark_data_lake_batch_write_skips_empty_data(mocker) -> None:
    service = SparkDatalakeRepository(mocker.Mock(), DataLakeEndpointModel(connection_name="example.datalake", bucket_name="bucket"))
    empty = mocker.Mock()
    empty.isEmpty.return_value = True

    service.write_batch(empty, "raw/path")

    assert not empty.persist.called



def test_spark_data_lake_components_use_canonical_uri(mocker) -> None:
    endpoint = DataLakeEndpointModel(connection_name="example.datalake", bucket_name="bucket")
    session = mocker.MagicMock()
    expected = object()
    session.read.parquet.return_value = expected
    assert SparkDatalakeIngestor(endpoint, session).ingest("/raw/data/") is expected
    assert session.read.parquet.call_args.args[0] == "s3a://bucket/raw/data"

    dataframe = mocker.MagicMock()
    service = SparkDatalakeRepository(session, endpoint)
    service.write(dataframe, "/raw/data/")
    assert dataframe.write.mode.return_value.parquet.call_args.args[0] == "s3a://bucket/raw/data"
    service.overwrite(dataframe, "raw/data")
    assert dataframe.write.mode.return_value.parquet.call_args.args[0] == "s3a://bucket/raw/data"
    assert service.read("raw/data") is expected
