from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID

import pandas as pd
import pytest

from data_platform.config.main_settings import settings
from data_platform.config.data_lake_environment import DataLakeEnvironment
from data_platform.util.kafka_utils import handle_kafka_response
from data_platform.transformer.value_transformer import (
    convert_to_integer,
    convert_to_optional_float,
    normalize_optional_text,
)
from data_platform.validation.dataframe_validator import validate_required_columns, validate_required_columns
from data_platform.util import csv_utils, database_utils, file_utils, log_utils, pipeline_utils, string_utils, \
    time_utils, path_utils as datalake_path_utils, spark_utils


class TestStringUtils:

    def test_should_be_not_none_rejects_none_value(self) -> None:
        with pytest.raises(ValueError):
            string_utils.should_not_be_none(None, "value")

    def test_should_not_be_none_or_empty_rejects_blank_text(self) -> None:
        with pytest.raises(ValueError):
            string_utils.should_not_be_none_or_empty("   ", "value")


class TestTimeUtils:

    def test_should_generate_ingestion_time_in_utc(self) -> None:
        actual = time_utils.generate_ingestion_time()

        assert actual.tzinfo is UTC

    def test_should_compute_elapsed_milliseconds(self, mocker) -> None:
        mocker.patch("data_platform.util.time_utils.time.perf_counter", return_value=3.5)

        actual = time_utils.elapsed_milliseconds(1.0)

        assert actual == 2500


class TestPipelineUtils:

    def test_should_create_uuid_string(self) -> None:
        actual = pipeline_utils.create_pipeline_id()

        UUID(actual)


class TestDatalakeUtils:

    def test_should_generate_paths(self, mocker) -> None:
        # Given
        given_time = datetime(2026, 8, 15, 12, 30, 45, 123456, tzinfo=UTC)
        mocker.patch.object(
            datalake_path_utils,
            "main_settings",
            SimpleNamespace(
                app=SimpleNamespace(dataset_name="Sale"),
                data_lake={
                    "data-platform.datalake": SimpleNamespace(
                        environment="dev",
                        scheme="s3a",
                        bucket_name="app-datalake",
                        audit_bucket_name="app-datalake-audit",
                    )
                },
            ),
        )

        # When
        actual_relative = datalake_path_utils.generate_relative_path(
            DataLakeEnvironment.RAW,
            given_time,
            "sale"
        )
        actual_full = datalake_path_utils.generate_full_path("bucket", "path/to/file")
        actual_datalake_uri = datalake_path_utils.generate_full_path(settings.data_lake["data-platform.datalake"].bucket_name, "path/to/file")
        actual_audit_uri = datalake_path_utils.generate_full_path(settings.data_lake["data-platform.datalake"].audit_bucket_name, "audit/file.json")

        # Then
        assert actual_relative.startswith("dev/raw/sale/")
        assert actual_full == "s3a://bucket/path/to/file"
        assert actual_datalake_uri == "s3a://app-datalake/path/to/file"
        assert actual_audit_uri == "s3a://app-datalake-audit/audit/file.json"

    def test_should_generate_relative_path_using_environment_defaults(self, mocker) -> None:
        # Given
        given_time = datetime(2026, 8, 15, 12, 30, 45, 123456, tzinfo=UTC)
        mocker.patch.object(
            datalake_path_utils,
            "main_settings",
            SimpleNamespace(
                app=SimpleNamespace(dataset_name="Sale"),
                data_lake={
                    "data-platform.datalake": SimpleNamespace(
                        environment="dev",
                        scheme="s3a",
                        bucket_name="app-datalake",
                        audit_bucket_name="app-datalake-audit",
                    )
                },
            ),
        )
        mocker.patch.object(datalake_path_utils, "datetime", SimpleNamespace(now=lambda tz=None: given_time))

        # When
        actual = datalake_path_utils.generate_relative_path(DataLakeEnvironment.RAW)

        # Then
        assert actual.startswith("dev/raw/sale/")

    def test_should_unpersist_persisted_dataframes_in_reverse_order(self, mocker) -> None:
        # Given
        given_first = mocker.Mock()
        given_second = mocker.Mock()

        # When
        with spark_utils.persisted_dataframes() as actual:
            actual.extend([given_first, given_second])

        # Then
        assert given_second.unpersist.call_count == 1
        assert given_first.unpersist.call_count == 1

    def test_should_raise_for_missing_paths(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            file_utils.generate_full_file_path(tmp_path / "missing")


class TestDatabaseUtils:

    def test_should_execute_all_sql_statements_and_commit(self, mocker) -> None:
        # Given
        given_connection = mocker.Mock()
        given_transaction_context = mocker.MagicMock()
        given_transaction_context.__enter__.return_value = given_connection
        given_connection.begin.return_value = given_transaction_context
        mock_create_connection = mocker.patch(
            "data_platform.util.database_utils.connection_registry.get_item",
            return_value=given_connection,
        )

        # When
        database_utils.execute_sql("sale.database", "select 1", "select 2")

        # Then
        assert mock_create_connection.call_count == 1
        assert given_connection.begin.call_count == 1
        assert given_connection.execute.call_count == 2
        assert given_connection.commit.call_count == 1


class TestDataFrameDefinitionValidation:

    def test_should_validate_required_columns_for_pandas_dataframe(self) -> None:
        # Given
        given_dataframe = pd.DataFrame({"id": [1], "name": ["sale"]})

        # When
        validate_required_columns(given_dataframe, frozenset({"id"}))

        # Then
        assert list(given_dataframe.columns) == ["id", "name"]

    def test_should_reject_missing_required_columns_for_pandas_dataframe(self) -> None:
        # Given
        given_dataframe = pd.DataFrame({"id": [1]})

        # When / Then
        with pytest.raises(ValueError):
            validate_required_columns(given_dataframe, frozenset({"id", "name"}))

    def test_should_reject_none_pandas_dataframe(self) -> None:
        with pytest.raises(ValueError):
            validate_required_columns(None, frozenset({"id"}))

    def test_should_validate_required_columns_for_spark_dataframe(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_dataframe.columns = ["id", "name"]

        # When
        validate_required_columns(given_dataframe, ["id"])

        # Then
        assert given_dataframe.columns == ["id", "name"]

    def test_should_reject_missing_required_columns_for_spark_dataframe(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_dataframe.columns = ["id"]

        # When / Then
        with pytest.raises(ValueError):
            validate_required_columns(given_dataframe, ["id", "name"])

    def test_should_reject_none_spark_dataframe(self) -> None:
        with pytest.raises(ValueError):
            validate_required_columns(None, ["id"])


class TestCsvUtils:

    def test_should_convert_and_normalize_values(self) -> None:
        assert convert_to_integer("12") == 12
        assert convert_to_optional_float("12.5") == 12.5
        assert convert_to_optional_float(" ") is None
        assert normalize_optional_text("  hello  ") == "hello"
        assert normalize_optional_text(None) is None

    def test_should_reject_empty_integer_values(self) -> None:
        with pytest.raises(ValueError):
            convert_to_integer("")

    def test_should_raise_on_missing_or_invalid_csv(self, tmp_path: Path) -> None:
        # Given
        given_missing = tmp_path / "missing.csv"
        given_empty = tmp_path / "empty.csv"
        given_empty.write_text("", encoding="utf-8")

        # When / Then
        with pytest.raises(FileNotFoundError):
            csv_utils.csv_to_dataframe(given_missing)

        with pytest.raises(ValueError):
            csv_utils.csv_to_dataframe(given_empty)

    def test_should_convert_invalid_integer_values(self) -> None:
        with pytest.raises(ValueError):
            convert_to_integer("abc")

    def test_should_return_none_for_invalid_optional_float(self) -> None:
        assert convert_to_optional_float("not-a-number") is None

    def test_should_normalize_blank_text_to_none(self) -> None:
        assert normalize_optional_text("   ") is None

    def test_should_raise_for_missing_column_only_csv(self, tmp_path: Path) -> None:
        # Given
        given_headers_only = tmp_path / "headers_only.csv"
        given_headers_only.write_text("id,name\n", encoding="utf-8")

        # When / Then
        with pytest.raises(ValueError):
            csv_utils.csv_to_dataframe(given_headers_only)

    def test_should_raise_for_invalid_csv_syntax(self, tmp_path: Path) -> None:
        # Given
        given_invalid = tmp_path / "invalid.csv"
        given_invalid.write_text('"id",name\n1,"broken\n', encoding="utf-8")

        # When / Then
        with pytest.raises(ValueError):
            csv_utils.csv_to_dataframe(given_invalid)


class TestLoggingAndStreaming:

    def test_should_configure_logging_and_write_log_line(self, mocker) -> None:
        # Given
        mock_basic_config = mocker.patch("data_platform.util.log_utils.logging.basicConfig")
        mock_logger_info = mocker.patch.object(log_utils.logger, "info")

        # When
        log_utils.configure_logging()
        log_utils.log_line()

        # Then
        assert mock_basic_config.call_count == 1
        assert mock_logger_info.call_count == 1

    def test_should_log_delivery_success_and_failure(self, mocker) -> None:
        # Given
        given_message = mocker.Mock()
        given_message.topic.return_value = "sale-events"
        mock_logger_info = mocker.patch.object(handle_kafka_response.__globals__["logger"], "info")
        mock_logger_error = mocker.patch.object(handle_kafka_response.__globals__["logger"], "error")

        # When
        handle_kafka_response(None, given_message, "event-001")
        handle_kafka_response(RuntimeError("boom"), given_message, "event-002")

        # Then
        assert mock_logger_info.call_count == 1
        assert mock_logger_error.call_count == 1
