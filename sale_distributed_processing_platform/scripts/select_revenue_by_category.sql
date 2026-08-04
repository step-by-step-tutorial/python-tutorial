SELECT category, sum(total_price) AS revenue
FROM sale_datawarehouse.sale_table
GROUP BY category
ORDER BY revenue DESC