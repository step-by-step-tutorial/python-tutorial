SELECT country, sum(total_price) AS revenue
FROM sale_datawarehouse.sale_table
GROUP BY country
ORDER BY revenue DESC