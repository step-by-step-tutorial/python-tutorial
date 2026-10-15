from collections.abc import Sequence
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402


def save_figure(figure: Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        figure.tight_layout()
        figure.savefig(path)
    finally:
        plt.close(figure)
    return path


def save_line_chart(labels: Sequence[str], values: Sequence[float], path: Path, x_label: str, y_label: str,
                    title: str) -> Path:
    figure, axes = plt.subplots()
    axes.plot(labels, values, marker="o")
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)
    axes.set_title(title)
    axes.tick_params(axis="x", labelrotation=45)
    return save_figure(figure, path)


def save_horizontal_bar_chart(labels: Sequence[str], values: Sequence[float], path: Path, x_label: str,
                              y_label: str, title: str) -> Path:
    figure, axes = plt.subplots()
    axes.barh(labels, values)
    axes.invert_yaxis()
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)
    axes.set_title(title)
    return save_figure(figure, path)
