import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
print(f"project root: {PROJECT_ROOT}")

CSV_PATH = Path(os.getenv("SALES_CSV_PATH", PROJECT_ROOT / "data" / "sales_data.csv"))
print(f"csv path: {CSV_PATH}")

OUTPUT_DIR = Path(os.getenv("SALES_OUTPUT_DIR", PROJECT_ROOT / "output"))
print(f"output dir: {OUTPUT_DIR}")

CLEANED_DATA_OUTPUT_PATH = OUTPUT_DIR / "cleaned_sales_data.csv"
REPORT_OUTPUT_PATH = OUTPUT_DIR / "sales_report.txt"
