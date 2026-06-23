from pathlib import Path

import pandas as pd


def read_csv(file_path: str) -> pd.DataFrame:
    return pd.read_csv(file_path)


def save_text_file(report: str, output_path: str) -> None:
    output_file = Path(output_path)
    with open(output_file, "w", encoding="utf-8") as file:
        file.write(report)
