from types import SimpleNamespace

import pytest

import data_platform.main as system_under_test


class TestRunPipeline:

    def test_should_instantiate_and_run_requested_pipeline(self, mocker) -> None:
        # Given
        given_dataset = SimpleNamespace(name="sale")
        given_pipeline_instance = mocker.Mock()
        given_pipeline_class = mocker.Mock(return_value=given_pipeline_instance)
        mock_dataset_lookup = mocker.patch.object(system_under_test.dataset_registry, "get_item", return_value=given_dataset)
        mocker.patch.dict(system_under_test.PIPELINES, {"inmemory": given_pipeline_class}, clear=True)
        mocker.patch.dict(system_under_test.DATASETS, {"sale": "sale"}, clear=True)

        # When
        system_under_test.run_pipeline("inmemory", "sale")

        # Then
        assert mock_dataset_lookup.call_count == 1
        assert given_pipeline_class.call_count == 1
        assert given_pipeline_instance.run.call_count == 1

    def test_should_raise_for_unknown_pipeline_or_dataset(self) -> None:
        # When / Then
        with pytest.raises(ValueError):
            system_under_test.run_pipeline("missing", "sale")

        with pytest.raises(ValueError):
            system_under_test.run_pipeline("inmemory", "missing")


class TestMain:

    def test_should_run_direct_pipeline_from_command_line_arguments(self, mocker) -> None:
        # Given
        mock_run_pipeline = mocker.patch.object(system_under_test, "run_pipeline")
        mocker.patch.object(system_under_test.sys, "argv", ["main.py", "inmemory", "sale"])

        # When
        system_under_test.main()

        # Then
        assert mock_run_pipeline.call_count == 1

    def test_should_exit_from_interactive_menu(self, mocker) -> None:
        # Given
        mock_run_pipeline = mocker.patch.object(system_under_test, "run_pipeline")
        mocker.patch.object(system_under_test.sys, "argv", ["main.py"])
        mocker.patch("builtins.input", side_effect=["0"])

        # When
        system_under_test.main()

        # Then
        assert mock_run_pipeline.call_count == 0

    def test_should_run_pipeline_from_interactive_menu(self, mocker) -> None:
        # Given
        mock_run_pipeline = mocker.patch.object(system_under_test, "run_pipeline")
        mocker.patch.object(system_under_test.sys, "argv", ["main.py"])
        mocker.patch("builtins.input", side_effect=["sale", "1", "0"])

        # When
        system_under_test.main()

        # Then
        assert mock_run_pipeline.call_count == 1
