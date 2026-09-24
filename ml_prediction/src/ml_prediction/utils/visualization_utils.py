from collections.abc import Sequence
from pathlib import Path

import matplotlib.pyplot as plt


def save_line_chart(
        labels: Sequence[str],
        values: Sequence[float],
        path: Path,
        x_label: str,
        y_label: str,
        title: str,
):
    figure, axes = plt.subplots()
    axes.plot(labels, values, marker="o")
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)
    axes.set_title(title)
    axes.tick_params(axis="x", labelrotation=45)
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        figure.savefig(path)
    finally:
        plt.close(figure)
    return path


def save_bar_chart(
        labels: Sequence[str],
        values: Sequence[float],
        path: Path,
        x_label: str,
        y_label: str,
        title: str,
        horizontal: bool = False,
):
    figure, axes = plt.subplots()
    if horizontal:
        axes.barh(labels, values)
        axes.invert_yaxis()
    else:
        axes.bar(labels, values)
        axes.tick_params(axis="x", labelrotation=45)
    axes.set_xlabel(x_label)
    axes.set_ylabel(y_label)
    axes.set_title(title)
    figure.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        figure.savefig(path)
    finally:
        plt.close(figure)
    return path
