from pathlib import Path

import pandas as pd
import pytest

from ml_prediction import cli
from ml_prediction.application.application import Application
from ml_prediction.presentation.prediction_presenter import PredictionPresenter
from ml_prediction.presentation.presenter import Presenter
from ml_prediction.presentation.training_presenter import TrainingPresenter


def test_application_delegates_train_and_predict(mocker) -> None:
    trainer = mocker.Mock()
    prediction_service = mocker.Mock()
    application = Application(mocker.Mock(), trainer, prediction_service)

    assert application.train() is trainer.train.return_value
    assert application.predict() is prediction_service.predict.return_value
    trainer.train.assert_called_once_with()
    prediction_service.predict.assert_called_once_with()


def test_presenters_implement_presenter_contract(tmp_path: Path) -> None:
    assert issubclass(TrainingPresenter, Presenter)
    assert issubclass(PredictionPresenter, Presenter)
    assert not TrainingPresenter.__abstractmethods__
    assert not PredictionPresenter.__abstractmethods__


def test_prediction_presenter_writes_predictions(tmp_path: Path, caplog) -> None:
    from ml_prediction.inference.prediction_service import PredictionOutput

    output_path = tmp_path / "output" / "predictions.csv"
    result = PredictionOutput(
        pd.DataFrame({"city": ["Paris"]}),
        pd.Series([123.5]),
        tmp_path / "house.csv",
    )

    assert PredictionPresenter(output_path).present(result) == output_path
    assert output_path.read_text(encoding="utf-8").splitlines() == [
        "city,predicted_total_price",
        "Paris,123.5",
    ]


def test_cli_parser_requires_dataset_and_prediction_together() -> None:
    with pytest.raises(SystemExit):
        cli.main(["house"])


def test_cli_select_dataset_retries_invalid_selection(monkeypatch, capsys) -> None:
    selections = iter(["invalid", "1"])
    monkeypatch.setattr("builtins.input", lambda _: next(selections))

    assert cli.select_dataset() == "house"
    assert "Select a number" in capsys.readouterr().out


def test_cli_select_prediction_supports_exit(monkeypatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "q")

    assert cli.select_prediction() is None


def test_cli_run_train_and_predict(mocker) -> None:
    application = mocker.Mock()
    mocker.patch.object(cli, "create_application", return_value=application)
    training_presenter = mocker.patch.object(cli, "TrainingPresenter")
    prediction_presenter = mocker.patch.object(cli, "PredictionPresenter")

    cli.run("house", "train")
    cli.run("house", "predict")

    application.train.assert_called_once_with()
    application.predict.assert_called_once_with()
    training_presenter.return_value.present.assert_called_once_with(application.train.return_value)
    prediction_presenter.return_value.present.assert_called_once_with(application.predict.return_value)


def test_cli_main_dispatches_direct_operation(mocker) -> None:
    run = mocker.patch.object(cli, "run")

    cli.main(["house", "predict"])

    run.assert_called_once_with("house", "predict")
