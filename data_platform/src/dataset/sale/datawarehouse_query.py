from util.file_utils import read_text_file


class Queries:
    TRUNCATE_DATAWAREHOUSE = read_text_file("truncate_datawarehouse.sql")
    SELECT_REVENUE_BY_CATEGORY = read_text_file("select_revenue_by_category.sql")
    SELECT_REVENUE_BY_COUNTRY = read_text_file("select_revenue_by_country.sql")
