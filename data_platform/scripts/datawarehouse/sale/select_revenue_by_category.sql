SELECT category, SUM(total_price) AS revenue
FROM app_datawarehouse.sale_table
GROUP BY category;
