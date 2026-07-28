SELECT country, sum(total_price) AS revenue
FROM sale_fact
GROUP BY country
ORDER BY revenue DESC
