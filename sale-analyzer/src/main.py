import logging

from src import config
from src.file_utils import read_csv, save_text_file
from src.cleaner_utils import clean_sales_data
from src.transform_utils import transform_sales_data
from src.report_service import build_report

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def main():
    logger.info(f"Loading sales data from: {config.RAW_DATA_FILE_PATH}")
    df = read_csv(config.RAW_DATA_FILE_PATH)

    logger.info(f"Cleaning sales data ({len(df)} rows)")
    df = clean_sales_data(df)

    logger.info(f"Transforming sales data ({len(df)} rows)")
    df = transform_sales_data(df)

    logger.info(f"Saving cleaned data to: {config.CLEANED_DATA_FILE_PATH}")
    df.to_csv(config.CLEANED_DATA_FILE_PATH, index=False)

    logger.info("Building sales analysis report")
    report = build_report(df)

    print(report)

    logger.info(f"Saving report to: {config.REPORT_FILE_PATH}")
    save_text_file(report, config.REPORT_FILE_PATH)

    logger.info("Sales data analysis pipeline completed successfully.")


if __name__ == "__main__":
    main()
