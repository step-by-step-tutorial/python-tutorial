INSERT INTO sale.sale_order (order_id, customer_id, order_date)
SELECT DISTINCT
    sale.sale_stage.order_id,
    sale.customer.customer_id,
    sale.sale_stage.order_date
FROM sale.sale_stage
JOIN sale.customer
    ON sale.customer.customer_name = sale.sale_stage.customer_name
   AND sale.customer.country = sale.sale_stage.country
ON CONFLICT (order_id) DO NOTHING;
