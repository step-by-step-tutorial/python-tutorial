SELECT address, AVG(price) AS average_price
FROM app_warehouse.house_table
GROUP BY address;
