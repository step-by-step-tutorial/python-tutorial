INSERT INTO sale.customer (customer_name, country)
SELECT DISTINCT customer_name, country
FROM sale.sale_stage
ON CONFLICT (customer_name, country) DO NOTHING;
