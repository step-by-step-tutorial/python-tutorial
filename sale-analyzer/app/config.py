import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

CSV_PATH = Path(os.getenv("SALES_CSV_PATH", PROJECT_ROOT / "data" / "sales_data.csv"))

OUTPUT_DIR = Path(os.getenv("SALES_OUTPUT_DIR", PROJECT_ROOT / "output"))

CLEANED_DATA_OUTPUT_PATH = OUTPUT_DIR / "cleaned_sales_data.csv"
REPORT_OUTPUT_PATH = OUTPUT_DIR / "sales_report.txt"
