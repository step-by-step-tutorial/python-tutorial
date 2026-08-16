from dataset.definition import Audit, Dataframe, DatabaseEndpoint, Dataset, FileEndpoint
from persistence.database import database_service as system_under_test


def build_dataset() -> Dataset:
    return Dataset(
        name="example",
        dataframe=Dataframe(schema=None, required_columns=frozenset()),
        audit=Audit(),
        processor_factories={},
        sources={
            "file": FileEndpoint(file_name="example.csv"),
        },
        destinations={
            "database": DatabaseEndpoint(
                table_name="sale.example_stage",
                before_load_sql_files=("before.sql",),
                after_load_sql_files=("after.sql",),
            ),
        },
    )


class TestPopulateStageTable:

    def test_should_dispatch_to_population_strategy(self, mocker) -> None:
        given_dataset = build_dataset()
        given_dataframe = mocker.MagicMock()
        mock_lookup_population_strategy = mocker.patch(
            "persistence.database.database_service.lookup_population_strategy"
        )
        mock_population_function = mocker.Mock()
        mock_lookup_population_strategy.return_value = mock_population_function

        system_under_test.populate_stage_table(given_dataset, given_dataframe)

        assert mock_lookup_population_strategy.call_count == 1
        assert mock_population_function.call_count == 1


class TestPopulate:

    def test_should_run_pre_sql_stage_population_and_post_sql(self, mocker) -> None:
        given_dataset = build_dataset()
        given_dataframe = mocker.MagicMock()
        mock_run_sql_files = mocker.patch.object(system_under_test, "run_sql_files")
        mock_populate_stage_table = mocker.patch.object(system_under_test, "populate_stage_table")

        system_under_test.populate(given_dataset, given_dataframe)

        assert mock_run_sql_files.call_count == 2
        assert mock_populate_stage_table.call_count == 1
