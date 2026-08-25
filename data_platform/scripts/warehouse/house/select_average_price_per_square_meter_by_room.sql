SELECT room, AVG(price_per_square_meter) AS average_price_per_square_meter
FROM app_warehouse.house_table
GROUP BY room;
