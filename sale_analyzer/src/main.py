import logging

import config
from file_utils import read_csv, save_text_file
from clean_data_service import clean_sale_data
from transform_service import transform_sale_data
from report_service import build_sale_report

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def main():
    logger.info(f"Loading sale data from: {config.RAW_SALE_DATA_FILE_PATH}")
    df = read_csv(config.RAW_SALE_DATA_FILE_PATH)

    logger.info(f"Cleaning sale data ({len(df)} rows)")
    df = clean_sale_data(df)

    logger.info(f"Transforming sale data ({len(df)} rows)")
    df = transform_sale_data(df)

    logger.info(f"Saving cleaned data to: {config.CLEANED_SALE_DATA_FILE_PATH}")
    df.to_csv(config.CLEANED_SALE_DATA_FILE_PATH, index=False)

    logger.info("Building sale analysis report")
    report = build_sale_report(df)

    print(report)

    logger.info(f"Saving report to: {config.SALE_REPORT_FILE_PATH}")
    save_text_file(report, config.SALE_REPORT_FILE_PATH)

    logger.info("sale data analysis pipeline completed successfully.")


if __name__ == "__main__":
    main()
