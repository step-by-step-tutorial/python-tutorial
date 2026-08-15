SELECT room, avg(price_per_square_meter) AS average_price_per_square_meter
FROM app_datawarehouse.house_table
GROUP BY room
