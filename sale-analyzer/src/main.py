from src import config
from src.csv_utils import read_csv
from src.cleaner_utils import clean_sales_data
from src.transformer import transform_sales_data
from src.reporter import build_report, save_report


def main():
    print("Loading data")
    df = read_csv(config.RAW_DATA_FILE_PATH)

    print("Cleaning data")
    df = clean_sales_data(df)

    print("Transforming data")
    df = transform_sales_data(df)

    print("Saving cleaned data")
    df.to_csv(config.CLEANED_DATA_FILE_PATH, index=False)

    print("Building report")
    report = build_report(df)

    print(report)

    print("Saving report")
    save_report(report, config.REPORT_FILE_PATH)

    print("Program finished successfully.")


if __name__ == "__main__":
    main()
