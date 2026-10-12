from datetime import date

import pandas as pd
import pytest

from data_platform.cleaner.inmemory_cleaner import BooleanColumnCleaner, FillMissingByColumnAverageCleaner, NumericColumnCleaner
from data_platform.config.key import Key
from data_platform.config.settings import settings
from data_platform.connector import database_connector, datalake_connector, kafka_connector
from data_platform.converter.value_converter import (
    convert_to_float,
    convert_to_integer,
    convert_to_optional_boolean,
    convert_to_optional_float,
)
from data_platform.pipeline.inmemory_pipeline import InmemoryPipeline
from data_platform.util import database_utils, dataframe_utils
from data_platform.util.airflow_utils import ensure_pipeline_success
from data_platform.connector.kafka_connector import ensure_topic_exists
from data_platform.util.validation_utils import (
    require_min_max,
    require_period_days,
    require_absent,
    require_blank,
    require_iso_date,
    require_key,
    require_item,
    require_xor,
    require_not_negative,
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
    create_engine = mocker.patch("data_platform.connector.database_connector.create_engine", return_value=engine)
    assert database_connector.create_database_engine(settings.database[Key.HOUSE_DATABASE]) is engine
    assert create_engine.call_args.args == (settings.database[Key.HOUSE_DATABASE].sqlalchemy_url,)

    s3 = object()
    client = mocker.patch("data_platform.connector.datalake_connector.boto3.client", return_value=s3)
    assert datalake_connector.create_datalake_client(settings.data_lake[Key.AUDIT_DATA_LAKE]) is s3
    assert client.call_args.kwargs["endpoint_url"] == settings.data_lake[Key.AUDIT_DATA_LAKE].endpoint

    producer = object()
    consumer = object()
    mocker.patch("data_platform.connector.kafka_connector.Producer", return_value=producer)
    mocker.patch("data_platform.connector.kafka_connector.Consumer", return_value=consumer)
    assert kafka_connector.create_producer(settings.messaging[Key.HOUSE_MESSAGING]) is producer
    assert kafka_connector.create_consumer(settings.messaging[Key.AUDIT_MESSAGING]) is consumer


def test_warehouse_connector_returns_configured_client(mocker) -> None:
    pytest.importorskip("clickhouse_connect")
    from data_platform.connector import warehouse_connector

    client = object()
    mocker.patch("data_platform.connector.warehouse_connector.clickhouse_connect.get_client", return_value=client)
    assert warehouse_connector.create_warehouse_client(settings.warehouse[Key.HOUSE_WAREHOUSE]) is client


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


def test_dataframe_helpers_handle_dict_rows_and_pandas_frames() -> None:
    assert dataframe_utils.row_to_dict({"id": 1}) == {"id": 1}
    with dataframe_utils.persisted_dataframes() as values:
        first, second = type("Frame", (), {"unpersist": lambda self: None})(), type("Frame", (), {"unpersist": lambda self: None})()
        values.extend([first, second])


def test_kafka_topic_and_airflow_helpers_handle_noop_and_failures(mocker) -> None:
    ensure_topic_exists("", "topic")
    admin = mocker.patch("data_platform.connector.kafka_connector.AdminClient")
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
        require_key({}, "missing")
    with pytest.raises(Exception):
        require_item((), "missing")
    with pytest.raises(Exception):
        require_absent(("present",), "present")
    with pytest.raises(Exception):
        require_min_max(2, 1)
    with pytest.raises(Exception):
        require_period_days(date(2026, 1, 2), date(2026, 1, 1))
    with pytest.raises(Exception):
        require_iso_date("invalid")
    with pytest.raises(Exception):
        require_xor(None, None)
    with pytest.raises(Exception):
        require_not_negative(-1)


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
    flow.after_step = lambda step: None
    dataset.flow = flow

    pipeline = InmemoryPipeline(dataset)
    pipeline.ingest = lambda: (_ for _ in ()).throw(RuntimeError("ingest failed"))
    with pytest.raises(RuntimeError, match="ingest failed"):
        pipeline.run()
    statuses = {call.args[0].status.value for call in mock_audit.emit.call_args_list}
    assert {"STARTED", "FAILED"}.issubset(statuses)
