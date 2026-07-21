INSERT INTO product (product_name, category)
SELECT DISTINCT product_name, category
FROM sale_stage
