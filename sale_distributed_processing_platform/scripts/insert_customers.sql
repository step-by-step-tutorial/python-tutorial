INSERT INTO customer (customer_name, country)
SELECT DISTINCT customer_name, country
FROM sale_stage
