SELECT category, sum(total_price) AS revenue
FROM sale_fact
GROUP BY category
ORDER BY revenue DESC
