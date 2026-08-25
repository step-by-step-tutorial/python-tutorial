import pandas as pd
import pytest

from data_platform.model import DatabaseEndpoint
from data_platform.repository.inmemory_database_repository import InmemoryDataframeRepository


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


class TestPandasDatabaseRepository:
    def test_should_save_dataframe(self, mocker) -> None:
        dataframe = mocker.Mock(spec=pd.DataFrame)
        engine = mocker.Mock()
        connection = mocker.Mock()
        transaction = mocker.MagicMock()
        transaction.__enter__.return_value = connection
        engine.begin.return_value = transaction
        get_item = mocker.patch(
            "data_platform.persistence.inmemory_database_repository.connection_registry.get_item",
            return_value=engine,
        )

        InmemoryDataframeRepository(build_endpoint()).write(dataframe)

        get_item.assert_called_once_with("sale.database")
        dataframe.to_sql.assert_called_once_with(
            name="example_stage", con=connection, schema="sale", if_exists="append", index=False
        )

    def test_should_propagate_save_error(self, mocker) -> None:
        dataframe = mocker.Mock(spec=pd.DataFrame)
        engine = mocker.Mock()
        transaction = mocker.MagicMock()
        engine.begin.return_value = transaction
        dataframe.to_sql.side_effect = RuntimeError("Pandas save failed")
        mocker.patch(
            "data_platform.persistence.inmemory_database_repository.connection_registry.get_item",
            return_value=engine,
        )

        with pytest.raises(RuntimeError, match="Pandas save failed"):
            InmemoryDataframeRepository(build_endpoint()).write(dataframe)

    def test_should_replace_dataframe(self, mocker) -> None:
        repository = InmemoryDataframeRepository(build_endpoint())
        truncate = mocker.patch.object(repository, "truncate_stage_table")
        save = mocker.patch.object(repository, "save")
        execute = mocker.patch.object(repository, "execute_files")

        repository.overwrite(mocker.Mock(spec=pd.DataFrame))

        truncate.assert_called_once()
        save.assert_called_once()
        execute.assert_called_once_with(["after.sql"])


