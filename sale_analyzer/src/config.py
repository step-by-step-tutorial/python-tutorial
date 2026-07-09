import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", PROJECT_ROOT / "output"))

RAW_DATA_FILE_PATH = Path(INPUT_DIR / "sales_data.csv")
CLEANED_DATA_FILE_PATH = OUTPUT_DIR / "cleaned_sales_data.csv"
REPORT_FILE_PATH = OUTPUT_DIR / "sales_report.txt"
