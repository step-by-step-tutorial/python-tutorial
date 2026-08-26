SELECT city, AVG(total_price) AS average_price
FROM app_warehouse.house_table
GROUP BY city;
