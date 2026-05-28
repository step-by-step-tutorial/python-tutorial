import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
print(f"project root: {PROJECT_ROOT}")

DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))
print(f"data dir: {DATA_DIR}")

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", PROJECT_ROOT / "output"))
print(f"output dir: {OUTPUT_DIR}")

RAW_DATA_FILE_PATH = Path(DATA_DIR / "sales_data.csv")
print(f"raw data file path: {RAW_DATA_FILE_PATH}")

CLEANED_DATA_FILE_PATH = OUTPUT_DIR / "cleaned_sales_data.csv"
print(f"clean data file path: {CLEANED_DATA_FILE_PATH}")

REPORT_FILE_PATH = OUTPUT_DIR / "sales_report.txt"
print(f"report file path: {REPORT_FILE_PATH}")
