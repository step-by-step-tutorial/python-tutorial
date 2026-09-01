from pathlib import Path

import pandas as pd
import pytest

from ml_prediction import main
from ml_prediction.application.application import Application
from ml_prediction.presentation.prediction_presenter import PredictionPresenter
from ml_prediction.presentation.presenter import Presenter
from ml_prediction.presentation.training_presenter import TrainingPresenter


def test_application_delegates_train_and_predict(mocker) -> None:
    trainer = mocker.Mock()
    dataset = mocker.Mock(dataset_name="house")
    prediction_service = mocker.Mock()
    mocker.patch(
        "ml_prediction.application.application.PredictionService",
        return_value=prediction_service,
    )
    application = Application(dataset, trainer, mocker.Mock())

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
    from ml_prediction.data_model.prediction import Prediction

    output_path = tmp_path / "output" / "predictions.csv"
    result = Prediction(
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
        main.main(["house"])


def test_cli_select_dataset_retries_invalid_selection(monkeypatch, capsys) -> None:
    selections = iter(["invalid", "1"])
    monkeypatch.setattr("builtins.input", lambda _: next(selections))

    assert main.select_dataset() == "house"
    assert "Select a number" in capsys.readouterr().out


def test_cli_select_prediction_supports_exit(monkeypatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "q")

    assert main.select_prediction() is None


def test_cli_run_train_and_predict(mocker) -> None:
    application = mocker.Mock()
    mocker.patch.object(main, "create_application", return_value=application)
    training_presenter = mocker.patch.object(main, "TrainingPresenter")
    prediction_presenter = mocker.patch.object(main, "PredictionPresenter")

    main.run("house", "train")
    main.run("house", "predict")

    application.train.assert_called_once_with()
    application.predict.assert_called_once_with()
    training_presenter.return_value.present.assert_called_once_with(application.train.return_value)
    prediction_presenter.return_value.present.assert_called_once_with(application.predict.return_value)


def test_create_application_does_not_load_model_for_training(mocker) -> None:
    predictor = mocker.patch.object(main, "HousePricePredictor")

    application = main.create_application("house", include_prediction=False)

    assert application.prediction_service is None
    predictor.assert_not_called()


def test_cli_main_dispatches_direct_operation(mocker) -> None:
    run = mocker.patch.object(main, "run")

    main.main(["house", "predict"])

    run.assert_called_once_with("house", "predict")


def test_cli_main_passes_search_flag(mocker) -> None:
    run = mocker.patch.object(main, "run")

    main.main(["house", "train", "--search"])

    run.assert_called_once_with("house", "train", True)
