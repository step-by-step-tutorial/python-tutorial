from datetime import date

import pandas as pd
import pytest

from data_platform.cleaners.cleaner_impl import BooleanColumnCleaner, FillMissingByColumnAverageCleaner, NumericColumnCleaner
from data_platform.config.keys import Key
from data_platform.connector import database_connections, datalake_connections, kafka_connections, warehouse_connections
from data_platform.converter.value_converter import (
    convert_to_float,
    convert_to_integer,
    convert_to_optional_boolean,
    convert_to_optional_float,
)
from data_platform.ingestion.spark_data_lake_ingestor import SparkDataLakeIngestor
from data_platform.pipeline.data_pipeline import DataPipeline
from data_platform.service.spark_data_lake_service import SparkDataLakeService
from data_platform.util import database_utils, dataframe_utils
from data_platform.util.airflow_utils import ensure_pipeline_success
from data_platform.util.dataframe_utils import empty_compatible_dataframe
from data_platform.util.kafka_admin import ensure_topic_exists
from data_platform.validators.data_validator_utils import (
    check_min_max,
    check_negative_days,
    require_absent,
    require_blank,
    require_iso_date,
    require_or_raise_map,
    require_or_raise_tuple,
    require_xor,
    should_not_be_negative,
)


def test_value_converters_cover_optional_and_invalid_inputs() -> None:
    assert convert_to_integer(True) == 1
    assert convert_to_integer(2.0) == 2
    assert convert_to_float(False) == 0.0
    assert convert_to_optional_float(12) == 12.0
    assert convert_to_optional_float("bad") is None
    assert convert_to_optional_boolean("YES") is True
    assert convert_to_optional_boolean("no") is False
    assert convert_to_optional_boolean(0) is False
    with pytest.raises(ValueError):
        convert_to_integer(2.5)
    with pytest.raises(ValueError):
        convert_to_float("")
    with pytest.raises(ValueError):
        convert_to_optional_boolean("maybe")


def test_cleaner_error_and_boolean_default_behavior() -> None:
    frame = pd.DataFrame({"flag": [None, "TRUE", "0"], "number": ["", "2", "bad"]})
    cleaned = BooleanColumnCleaner("flag", default_value=True).clean(frame)
    assert cleaned["flag"].tolist() == [True, True, False]
    assert NumericColumnCleaner("number", default_value=7).clean(frame)["number"].tolist() == [7.0, 2.0, 7.0]
    with pytest.raises(ValueError):
        FillMissingByColumnAverageCleaner("number").clean(pd.DataFrame({"number": [None]}))


def test_connector_factories_return_configured_clients(mocker) -> None:
    engine = object()
    mocker.patch("data_platform.connector.database_connections.create_engine", return_value=engine)
    assert database_connections.create_house_connection() is engine
    assert database_connections.create_online_shopping_connection() is engine
    assert database_connections.create_audit_connection() is engine

    s3 = object()
    mocker.patch("data_platform.connector.datalake_connections.boto3.client", return_value=s3)
    assert datalake_connections.create_house_connection() is s3
    assert datalake_connections.create_audit_connection() is s3
    assert datalake_connections.create_online_shopping_connection() is s3

    producer = object()
    consumer = object()
    mocker.patch("data_platform.connector.kafka_connections.Producer", return_value=producer)
    mocker.patch("data_platform.connector.kafka_connections.Consumer", return_value=consumer)
    assert kafka_connections.create_house_publisher_connection() is producer
    assert kafka_connections.create_audit_publisher_connection() is producer
    assert kafka_connections.create_house_listener_connection() is consumer
    assert kafka_connections.create_audit_listener_connection() is consumer

    client = object()
    mocker.patch("data_platform.connector.warehouse_connections.clickhouse_connect.get_client", return_value=client)
    assert warehouse_connections.create_house_connection() is client
    assert warehouse_connections.create_online_shopping_connection() is client
    assert warehouse_connections.create_audit_connection() is client


def test_database_utilities_execute_and_return_rows(mocker) -> None:
    connection = mocker.Mock()
    context = mocker.MagicMock()
    context.__enter__.return_value = connection
    connection_registry = mocker.patch("data_platform.util.database_utils.connection_registry.get_item")
    connection_registry.return_value.begin.return_value = context
    result = mocker.Mock()
    result.mappings.return_value.all.return_value = [{"id": 1}]
    connection.execute.return_value = result

    assert database_utils.execute_select_query("db", "select 1") == ({"id": 1},)
    database_utils.execute_query_strings("db", ("one", "two"))
    assert connection.execute.call_args_list[-2].args[0].text == "one"
    assert connection.execute.call_args_list[-1].args[0].text == "two"


def test_spark_data_lake_components_use_canonical_uri(mocker) -> None:
    endpoint = type("Endpoint", (), {"scheme": "s3a", "bucket_name": "bucket"})()
    session = mocker.MagicMock()
    expected = object()
    session.read.parquet.return_value = expected
    assert SparkDataLakeIngestor(endpoint, session).ingest("/raw/data/") is expected
    assert session.read.parquet.call_args.args[0] == "s3a://bucket/raw/data"

    dataframe = mocker.MagicMock()
    service = SparkDataLakeService(session, endpoint)
    service.write(dataframe, "/raw/data/")
    assert dataframe.write.mode.return_value.parquet.call_args.args[0] == "s3a://bucket/raw/data"
    service.overwrite(dataframe, "raw/data")
    assert dataframe.write.mode.return_value.parquet.call_args.args[0] == "s3a://bucket/raw/data"
    assert service.read("raw/data") is expected


def test_dataframe_helpers_handle_dict_rows_and_pandas_frames() -> None:
    assert dataframe_utils.row_to_dict({"id": 1}) == {"id": 1}
    assert dataframe_utils.empty_compatible_dataframe(pd.DataFrame({"id": [1]})).empty
    with dataframe_utils.persisted_dataframes() as values:
        first, second = type("Frame", (), {"unpersist": lambda self: None})(), type("Frame", (), {"unpersist": lambda self: None})()
        values.extend([first, second])


def test_kafka_admin_and_airflow_helpers_handle_noop_and_failures(mocker) -> None:
    ensure_topic_exists("", "topic")
    admin = mocker.patch("data_platform.util.kafka_admin.AdminClient")
    ensure_topic_exists("broker", "topic")
    assert admin.return_value.create_topics.return_value["topic"] is not None

    task = type("Task", (), {"task_id": "final"})()
    dag_run = type("DagRun", (), {"get_task_instances": lambda self: [type("TI", (), {"task_id": "upstream", "state": "success"})()]})()
    ensure_pipeline_success(task=task, dag_run=dag_run)
    failed = type("DagRun", (), {"get_task_instances": lambda self: [type("TI", (), {"task_id": "upstream", "state": "failed"})()]})()
    with pytest.raises(Exception):
        ensure_pipeline_success(task=task, dag_run=failed)

    task_instance = type("TaskInstance", (), {
        "get_task_states": lambda self, **_: {"upstream": "failed", "final": "success"}
    })()
    modern_dag_run = type("DagRun", (), {"dag_id": "example", "run_id": "run-1"})()
    with pytest.raises(Exception):
        ensure_pipeline_success(task=task, dag_run=modern_dag_run, task_instance=task_instance)
    task_states_with_details = type("TaskInstance", (), {
        "get_task_states": lambda self, **_: {
            "upstream": {"state": "failed"},
            "final": {"state": "success"},
        }
    })()
    with pytest.raises(Exception):
        ensure_pipeline_success(task=task, dag_run=modern_dag_run, task_instance=task_states_with_details)


def test_validator_utility_rejects_invalid_contracts() -> None:
    with pytest.raises(Exception):
        require_blank("value")
    with pytest.raises(Exception):
        require_or_raise_map({}, "missing")
    with pytest.raises(Exception):
        require_or_raise_tuple((), "missing")
    with pytest.raises(Exception):
        require_absent(("present",), "present")
    with pytest.raises(Exception):
        check_min_max(2, 1)
    with pytest.raises(Exception):
        check_negative_days(date(2026, 1, 2), date(2026, 1, 1))
    with pytest.raises(Exception):
        require_iso_date("invalid")
    with pytest.raises(Exception):
        require_xor(None, None)
    with pytest.raises(Exception):
        should_not_be_negative(-1)


def test_pipeline_reports_failure_and_still_cleans_up(mocker) -> None:
    mock_audit = mocker.Mock()
    mocker.patch("data_platform.pipeline.pipeline.AuditService", return_value=mock_audit)
    dataset = mocker.Mock(name="dataset")
    dataset.name = "example"
    dataset.audit = mocker.Mock()
    flow = mocker.Mock()
    flow.before_pipeline = lambda pipeline: None
    flow.after_pipeline = lambda pipeline: None
    flow.before_step = lambda step: None
    flow.after_stage = lambda step: None
    dataset.flow = flow

    pipeline = DataPipeline(dataset)
    pipeline.ingest = lambda: (_ for _ in ()).throw(RuntimeError("ingest failed"))
    with pytest.raises(RuntimeError, match="ingest failed"):
        pipeline.run()
    statuses = {call.args[0].status.value for call in mock_audit.emit.call_args_list}
    assert {"STARTED", "FAILED"}.issubset(statuses)
