INSERT INTO sale.order_item (order_id, product_id, quantity, unit_price, total_price)
SELECT sale.sale_stage.order_id,
       sale.product.product_id,
       sale.sale_stage.quantity,
       sale.sale_stage.unit_price,
       sale.sale_stage.total_price
FROM sale.sale_stage
         JOIN sale.product
              ON sale.product.product_name = sale.sale_stage.product_name
                 AND sale.product.category = sale.sale_stage.category
ON CONFLICT (order_id, product_id) DO UPDATE
    SET quantity = EXCLUDED.quantity,
        unit_price = EXCLUDED.unit_price,
        total_price = EXCLUDED.total_price;
