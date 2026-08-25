SELECT country, SUM(total_price) AS revenue
FROM app_warehouse.sale_table
GROUP BY country;
