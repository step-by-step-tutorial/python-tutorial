import pytest

from data_platform.model.endpoints import DatabaseEndpoint
from data_platform.repository.spark_database_repository import SparkDatabaseRepository


def build_endpoint() -> DatabaseEndpoint:
    return DatabaseEndpoint(
        connection_name="sale.database",
        schema="sale",
        stage_table_name="example_stage",
        full_stage_table_name="sale.example_stage",
        table_names=["sale.example_stage"],
        create_sql_files={},
        truncate_sql_files={"truncate": "before.sql"},
        write_sql_files={"after": "after.sql"},
        query_sql_files={},
    )


class TestSparkDatabaseRepository:
    def test_should_save_dataframe(self, mocker) -> None:
        dataframe = mocker.Mock()
        writer = mocker.Mock()
        dataframe.write = writer
        writer.format.return_value = writer
        writer.option.return_value = writer
        writer.mode.return_value = writer

        SparkDatabaseRepository(build_endpoint()).write(dataframe)

        writer.format.assert_called_once_with("jdbc")
        assert writer.option.call_count == 5
        writer.mode.assert_called_once_with("append")
        writer.save.assert_called_once()

    def test_should_propagate_save_error(self, mocker) -> None:
        dataframe = mocker.Mock()
        writer = mocker.Mock()
        dataframe.write = writer
        writer.format.return_value = writer
        writer.option.return_value = writer
        writer.mode.return_value = writer
        writer.save.side_effect = RuntimeError("Spark save failed")

        with pytest.raises(RuntimeError, match="Spark save failed"):
            SparkDatabaseRepository(build_endpoint()).write(dataframe)

    def test_should_replace_dataframe(self, mocker) -> None:
        repository = SparkDatabaseRepository(build_endpoint())
        truncate = mocker.patch.object(repository, "truncate_stage_table")
        write = mocker.patch.object(repository, "write")
        execute = mocker.patch.object(repository, "execute_query_files")

        repository.overwrite(mocker.Mock())

        truncate.assert_called_once()
        write.assert_called_once()
        execute.assert_called_once_with(("after.sql",))
