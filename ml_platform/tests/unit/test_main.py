import pytest

from ml_platform import main
from ml_platform.config.operation import Operation


def test_parser_reads_dataset_operation_and_search() -> None:
    args = main.create_parser().parse_args(["house", "train", "--search"])

    assert (args.dataset, args.operation, args.search) == ("house", Operation.TRAIN, True)


def test_main_runs_the_requested_operation(mocker) -> None:
    run = mocker.patch.object(main, "run")

    main.main(["online_shopping", "predict"])

    run.assert_called_once_with("online_shopping", Operation.PREDICT, False)


def test_run_dispatches_to_trainer_and_predictor(mocker) -> None:
    trainer = mocker.patch.object(main, "Trainer")
    predictor = mocker.patch.object(main, "Predictor")

    main.run("house", Operation.TRAIN)
    main.run("house", Operation.PREDICT)

    trainer.return_value.train.assert_called_once_with()
    predictor.return_value.predict.assert_called_once_with()


def test_main_requires_dataset_and_operation_together() -> None:
    with pytest.raises(SystemExit, match="must be provided together"):
        main.main(["house"])


def test_main_requires_arguments_without_interactive_input(mocker) -> None:
    mocker.patch.object(main.sys.stdin, "isatty", return_value=False)

    with pytest.raises(RuntimeError, match="not interactive"):
        main.main([])


def test_select_returns_chosen_option(monkeypatch: pytest.MonkeyPatch) -> None:
    answers = iter(["5", "2"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    assert main.select("dataset", ("house", "online_shopping")) == "online_shopping"


def test_select_exits_on_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("builtins.input", lambda _: "0")

    assert main.select("dataset", ("house",)) is None
