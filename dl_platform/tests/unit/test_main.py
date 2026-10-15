import pytest

from dl_platform import main


def test_parser_reads_the_task() -> None:
    assert main.create_parser().parse_args(["animal_detection"]).task == "animal_detection"


def test_parser_rejects_unknown_tasks() -> None:
    with pytest.raises(SystemExit):
        main.create_parser().parse_args(["face_detection"])


def test_main_runs_the_requested_task(mocker) -> None:
    run = mocker.patch.object(main, "run")

    main.main(["person_detection"])

    run.assert_called_once_with("person_detection", main.Operation.DETECT)


def test_main_runs_the_requested_operation(mocker) -> None:
    run = mocker.patch.object(main, "run")

    main.main(["animal_detection", "evaluate"])

    run.assert_called_once_with("animal_detection", main.Operation.EVALUATE)


def test_run_uses_the_task_settings(mocker) -> None:
    runner = mocker.patch.object(main, "DetectionRunner")

    main.run("vehicle_detection")

    assert runner.call_args.args[0].task.name == "vehicle_detection"
    runner.return_value.run.assert_called_once_with()


def test_run_evaluates_the_task(mocker) -> None:
    evaluator = mocker.patch.object(main, "DetectionEvaluator")

    main.run("person_detection", main.Operation.EVALUATE)

    assert evaluator.call_args.args[0].task.name == "person_detection"
    evaluator.return_value.evaluate.assert_called_once_with()


def test_main_requires_a_task_without_interactive_input(mocker) -> None:
    mocker.patch.object(main.sys.stdin, "isatty", return_value=False)

    with pytest.raises(RuntimeError, match="not interactive"):
        main.main([])


def test_select_returns_the_chosen_option(monkeypatch: pytest.MonkeyPatch) -> None:
    answers = iter(["9", "2"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))

    assert main.select("task", ("vehicle_detection", "person_detection")) == "person_detection"
