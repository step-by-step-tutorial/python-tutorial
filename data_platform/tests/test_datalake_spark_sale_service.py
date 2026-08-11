import pytest

from service.datalake import distributed_datalake_service as system_under_test


class TestOverwrite:

    def test_should_overwrite_dataframe_as_parquet_without_partition_columns(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_dataframe.columns = ["order_id", "order_date", "country"]
        given_writer = given_dataframe.write
        given_bucket_name = "sale-bucket"
        given_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"

        given_writer.mode.return_value = given_writer

        # When
        system_under_test.overwrite(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert given_writer.mode.call_count == 1
        assert given_writer.mode.call_args.args == ("overwrite",)
        assert given_writer.parquet.call_count == 1
        assert given_writer.parquet.call_args.args == (f"s3a://{given_bucket_name}/{given_path}",)

    def test_should_raise_error_when_dataframe_is_none(self) -> None:
        # Given
        given_dataframe = None
        given_bucket_name = "sale-bucket"
        given_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.overwrite(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual.value is not None


    def test_should_raise_error_when_bucket_name_is_empty(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_bucket_name = " "
        given_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.overwrite(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual.value is not None
        assert given_dataframe.write.mode.call_count == 0
        assert given_dataframe.write.parquet.call_count == 0

    def test_should_raise_error_when_path_is_none(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_bucket_name = "sale-bucket"
        given_path = None

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.overwrite(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual.value is not None
        assert given_dataframe.write.mode.call_count == 0
        assert given_dataframe.write.partitionBy.call_count == 0
        assert given_dataframe.write.parquet.call_count == 0

    def test_should_raise_error_when_path_is_empty(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_bucket_name = "sale-bucket"
        given_path = " "

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.overwrite(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual.value is not None
        assert given_dataframe.write.mode.call_count == 0
        assert given_dataframe.write.partitionBy.call_count == 0
        assert given_dataframe.write.parquet.call_count == 0

    def test_should_propagate_error_when_setting_write_mode_fails(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_dataframe.columns = ["order_id"]
        given_writer = given_dataframe.write
        given_bucket_name = "sale-bucket"
        given_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_error_message = "Cannot set write mode"

        given_writer.mode.side_effect = RuntimeError(given_error_message)

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.overwrite(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual.value is not None
        assert given_writer.mode.call_count == 1
        assert given_writer.parquet.call_count == 0

    def test_should_propagate_error_when_parquet_writing_without_partitions_fails(self, mocker) -> None:
        # Given
        given_dataframe = mocker.Mock()
        given_dataframe.columns = ["order_id"]
        given_writer = given_dataframe.write
        given_bucket_name = "sale-bucket"
        given_path = "dev/raw/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_error_message = "Parquet writing failed"

        given_writer.mode.return_value = given_writer
        given_writer.parquet.side_effect = RuntimeError(given_error_message)

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.overwrite(dataframe=given_dataframe, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual.value is not None
        assert given_writer.mode.call_count == 1
        assert given_writer.parquet.call_count == 1
        assert given_writer.parquet.call_args.args == (f"s3a://{given_bucket_name}/{given_path}",)


class TestRead:

    def test_should_read_parquet_dataframe_from_given_uri(self, mocker) -> None:
        # Given
        given_session = mocker.Mock()
        given_bucket_name = "sale-bucket"
        given_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_dataframe = mocker.Mock()

        given_session.read.parquet.return_value = given_dataframe

        # When
        actual = system_under_test.read(session=given_session, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual is given_dataframe
        assert given_session.read.parquet.call_count == 1
        assert given_session.read.parquet.call_args.args == (f"s3a://{given_bucket_name}/{given_path}",)

    def test_should_raise_error_when_session_is_none(self) -> None:
        # Given
        given_session = None
        given_bucket_name = "sale-bucket"
        given_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.read(session=given_session, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual.value is not None


    def test_should_raise_error_when_bucket_name_is_empty(self, mocker) -> None:
        # Given
        given_session = mocker.Mock()
        given_bucket_name = " "
        given_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.read(session=given_session, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual.value is not None
        assert given_session.read.parquet.call_count == 0

    def test_should_raise_error_when_path_is_none(self, mocker) -> None:
        # Given
        given_session = mocker.Mock()
        given_bucket_name = "sale-bucket"
        given_path = None

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.read(session=given_session, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual.value is not None
        assert given_session.read.parquet.call_count == 0

    def test_should_raise_error_when_path_is_empty(self, mocker) -> None:
        # Given
        given_session = mocker.Mock()
        given_bucket_name = "sale-bucket"
        given_path = " "

        # When
        with pytest.raises(ValueError) as actual:
            system_under_test.read(session=given_session, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual.value is not None
        assert given_session.read.parquet.call_count == 0

    def test_should_propagate_error_when_parquet_reading_fails(self, mocker) -> None:
        # Given
        given_session = mocker.Mock()
        given_bucket_name = "sale-bucket"
        given_path = "dev/enriched/sale/ingestion_year=2026/ingestion_month=08/ingestion_day=04"
        given_error_message = "Parquet reading failed"

        given_session.read.parquet.side_effect = RuntimeError(given_error_message)

        # When
        with pytest.raises(RuntimeError) as actual:
            system_under_test.read(session=given_session, bucket_name=given_bucket_name, path=given_path)

        # Then
        assert actual.value is not None
        assert given_session.read.parquet.call_count == 1
        assert given_session.read.parquet.call_args.args == (f"s3a://{given_bucket_name}/{given_path}",)