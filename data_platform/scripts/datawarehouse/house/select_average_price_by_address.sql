SELECT address, avg(price) AS average_price
FROM app_datawarehouse.house_table
GROUP BY address
