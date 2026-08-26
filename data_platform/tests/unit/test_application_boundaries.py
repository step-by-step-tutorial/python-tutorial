import sys

import pandas as pd
import pytest

from data_platform import main as application
from data_platform.connector import spark_session_factory
from data_platform.presentation import dataframe_display
from data_platform.repository.database_repository import DatabaseRepository
from data_platform.repository.spark_database_repository import SparkDatabaseRepository
from data_platform.service.spark_data_lake_service import SparkDataLakeService
from data_platform.util import csv_utils


def test_main_selects_a_registered_dataset(monkeypatch, mocker) -> None:
    mocker.patch.object(application.dataset_registry, "names", return_value=("house", "online_shopping"))
    selections = iter(("invalid", "2"))
    monkeypatch.setattr("builtins.input", lambda _: next(selections))

    assert application.select_dataset() == "online_shopping"


def test_main_runs_explicit_dataset(monkeypatch, mocker) -> None:
    pipeline = mocker.Mock()
    mocker.patch.object(application, "DataPipeline", return_value=pipeline)
    dataset = object()
    mocker.patch.object(application.dataset_registry, "get_item", return_value=dataset)
    monkeypatch.setattr(sys, "argv", ["data_platform.main", "house"])

    application.main()

    assert application.dataset_registry.get_item("house") is dataset
    assert pipeline.run.called


def test_main_rejects_headless_execution_without_dataset(monkeypatch) -> None:
    monkeypatch.setattr(sys, "argv", ["data_platform.main"])
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)

    with pytest.raises(RuntimeError, match="dataset name is required"):
        application.main()


def test_display_helpers_forward_data_to_displayers(mocker) -> None:
    display = mocker.patch.object(dataframe_display, "show")
    dataframe_display.show_map_of_dataframe({"summary": pd.DataFrame({"value": [1]})})
    assert display.call_args.args[0]["value"].tolist() == [1]

    spark_frame = mocker.Mock()
    dataframe_display.show_spark_dataframes({"summary": spark_frame})
    assert spark_frame.show.called


def test_spark_session_factory_reuses_active_session(mocker) -> None:
    active_session = mocker.Mock()
    mocker.patch.object(spark_session_factory.SparkSession, "getActiveSession", return_value=active_session)
    mocker.patch.object(spark_session_factory, "_is_session_active", return_value=True)

    assert spark_session_factory.create_session() is active_session


def test_spark_session_factory_detects_stopped_or_invalid_sessions(mocker) -> None:
    stopped = mocker.Mock()
    stopped.sparkContext._jsc.sc.return_value.isStopped.return_value = True
    assert spark_session_factory._is_session_active(stopped) is False
    assert spark_session_factory._is_session_active(object()) is False


def test_database_repositories_delegate_query_and_write_operations(mocker) -> None:
    select = mocker.patch("data_platform.repository.database_repository.execute_select_query", return_value=(("row",),))
    execute = mocker.patch("data_platform.repository.database_repository.execute_query_files")
    repository = DatabaseRepository(type("Endpoint", (), {"connection_name": "db"})())
    assert repository.find_by_query("select") == (("row",),)
    repository.execute_query_files(("one.sql",))
    assert select.call_args.args == ("db", "select")
    assert execute.call_args.args == ("db", ("one.sql",))

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
    service = SparkDataLakeService(mocker.Mock(), type("Endpoint", (), {"scheme": "s3a", "bucket_name": "bucket"})())
    empty = mocker.Mock()
    empty.isEmpty.return_value = True

    service.write_batch(empty, "raw/path")

    assert not empty.persist.called


def test_csv_utils_reports_missing_empty_and_unreadable_files(tmp_path) -> None:
    missing = tmp_path / "missing.csv"
    with pytest.raises(FileNotFoundError):
        csv_utils.csv_to_dataframe(str(missing))

    empty = tmp_path / "empty.csv"
    empty.write_text("id,name\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no data rows"):
        csv_utils.csv_to_dataframe(str(empty))

    invalid = tmp_path / "invalid.csv"
    invalid.write_bytes(b"\x80")
    with pytest.raises(ValueError, match="Unable to read CSV"):
        csv_utils.csv_to_dataframe(str(invalid))
