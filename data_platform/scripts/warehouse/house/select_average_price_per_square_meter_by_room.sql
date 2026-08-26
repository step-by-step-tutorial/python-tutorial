SELECT property_type, AVG(price_per_sqm) AS average_price_per_sqm
FROM app_warehouse.house_table
GROUP BY property_type;
