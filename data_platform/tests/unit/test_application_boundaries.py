import sys

import pandas as pd
import pytest

from data_platform import main as application
from data_platform.repository.inmemory_database_repository import InmemoryDatabaseRepository
from data_platform.util import csv_utils, display_utils


def test_main_selects_a_registered_dataset(monkeypatch, mocker) -> None:
    mocker.patch.object(application.dataset_registry, "names", return_value=("house", "online_shopping"))
    selections = iter(("invalid", "2"))
    monkeypatch.setattr("builtins.input", lambda _: next(selections))

    assert application.select_dataset() == "online_shopping"


def test_main_runs_explicit_dataset(monkeypatch, mocker) -> None:
    pipeline = mocker.Mock()
    pipeline_class = mocker.patch.object(application, "InmemoryPipeline", return_value=pipeline)
    dataset = object()
    create_dataset = mocker.patch.object(application.dataset_registry, "create_dataset", return_value=dataset)

    application.main(["house", "inmemory"])

    assert create_dataset.call_args.args == ("house", application.PipelineType.INMEMORY)
    assert pipeline_class.call_args.args == (dataset,)
    assert pipeline.run.called


def test_main_rejects_headless_execution_without_dataset(monkeypatch) -> None:
    monkeypatch.setattr(sys.stdin, "isatty", lambda: False)

    with pytest.raises(RuntimeError, match="dataset name and pipeline type are required"):
        application.main([])


def test_display_helpers_forward_data_to_displayers(mocker) -> None:
    display = mocker.patch.object(display_utils, "show")
    display_utils.show_map_of_dataframe({"summary": pd.DataFrame({"value": [1]})})
    assert display.call_args.args[0]["value"].tolist() == [1]

    spark_frame = mocker.Mock()
    display_utils.show_spark_dataframes({"summary": spark_frame})
    assert spark_frame.show.called





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


def test_database_repositories_delegate_query_and_write_operations(mocker) -> None:
    select = mocker.patch("data_platform.repository.inmemory_database_repository.execute_select_query", return_value=(("row",),))
    execute = mocker.patch("data_platform.repository.inmemory_database_repository.execute_query_files")
    repository = InmemoryDatabaseRepository(type("Endpoint", (), {"connection_name": "db"})())
    assert repository.find_by_query("select") == (("row",),)
    repository.execute_query_files(("one.sql",))
    assert select.call_args.args == ("db", "select")
    assert execute.call_args.args == ("db", ("one.sql",))
