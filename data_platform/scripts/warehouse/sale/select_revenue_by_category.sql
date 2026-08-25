SELECT category, SUM(total_price) AS revenue
FROM app_warehouse.sale_table
GROUP BY category;
