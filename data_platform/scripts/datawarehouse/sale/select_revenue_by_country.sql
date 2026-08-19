SELECT country, SUM(total_price) AS revenue
FROM app_datawarehouse.sale_table
GROUP BY country;
