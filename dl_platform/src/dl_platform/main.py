import argparse
import logging
import sys
from collections.abc import Sequence

from dl_platform.config.detection_tasks import DETECTION_TASKS
from dl_platform.inference.detection_runner import DetectionRunner
from dl_platform.model.settings_model import SettingsModel

TASKS = tuple(DETECTION_TASKS)


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run a deep learning vision task on a folder of images.")
    parser.add_argument("task", nargs="?", choices=TASKS, help="Task name.")
    return parser


def run(task_name: str) -> None:
    DetectionRunner(SettingsModel.from_env(DETECTION_TASKS[task_name])).run()


def select(title: str, options: Sequence[str]) -> str | None:
    print(f"Available {title}s:")
    for index, option in enumerate(options, start=1):
        print(f"  {index}. {option}")
    print("  0. Exit")

    while True:
        selection = input(f"Select a {title}: ").strip().lower()
        if selection in {"0", "q", "quit", "exit"}:
            return None
        if selection.isdigit() and 1 <= int(selection) <= len(options):
            return options[int(selection) - 1]
        print(f"Select a number between 1 and {len(options)}, or 0 to exit.")


def main(argv: Sequence[str] | None = None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    args = create_parser().parse_args(argv)

    if args.task is not None:
        run(args.task)
        return

    if not sys.stdin.isatty():
        raise RuntimeError("task is required when standard input is not interactive")

    task_name = select("task", TASKS)
    if task_name is not None:
        run(task_name)


if __name__ == "__main__":
    main()
