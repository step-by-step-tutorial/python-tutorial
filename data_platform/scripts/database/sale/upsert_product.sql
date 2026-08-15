INSERT INTO sale.product (product_name, category)
SELECT DISTINCT product_name, category
FROM sale.sale_stage ON CONFLICT (product_name, category) DO NOTHING;
