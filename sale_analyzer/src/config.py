import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", PROJECT_ROOT / "output"))

RAW_SALE_DATA_FILE_PATH = Path(INPUT_DIR / "sale_data.csv")
CLEANED_SALE_DATA_FILE_PATH = OUTPUT_DIR / "cleaned_sale_data.csv"
SALE_REPORT_FILE_PATH = OUTPUT_DIR / "sale_report.txt"
