from util.file_utils import read_sql_file


class Queries:
    TRUNCATE_DATAWAREHOUSE = read_sql_file("truncate_datawarehouse.sql")
    SELECT_REVENUE_BY_CATEGORY = read_sql_file("select_revenue_by_category.sql")
    SELECT_REVENUE_BY_COUNTRY = read_sql_file("select_revenue_by_country.sql")
