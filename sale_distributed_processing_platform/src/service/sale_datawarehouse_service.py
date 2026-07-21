from pandas import DataFrame

from factory import datawarehouse_connection_factory


def populate(data_frame: DataFrame, ) -> None:
    with datawarehouse_connection_factory.create_connection() as connection:
        connection.command("TRUNCATE TABLE sale_fact")
        connection.insert_df("sale_fact", data_frame)


def get_revenue_by_category():
    with datawarehouse_connection_factory.create_connection() as connection:
        return connection.query_df(
            '''
            SELECT category, sum(total_price) AS revenue
            FROM sale_fact
            GROUP BY category
            ORDER BY revenue DESC
            '''
        )


def get_revenue_by_country():
    with datawarehouse_connection_factory.create_connection() as connection:
        return connection.query_df(
            '''
            SELECT country, sum(total_price) AS revenue
            FROM sale_fact
            GROUP BY country
            ORDER BY revenue DESC
            '''
        )
