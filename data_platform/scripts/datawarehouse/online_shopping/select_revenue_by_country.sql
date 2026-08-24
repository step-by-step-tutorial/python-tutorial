SELECT country, sum(net_revenue) AS revenue FROM app_datawarehouse.online_shopping_table GROUP BY country ORDER BY revenue DESC;
