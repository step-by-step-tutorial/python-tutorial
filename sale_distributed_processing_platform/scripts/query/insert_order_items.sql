INSERT INTO order_item (order_id, product_id, quantity, unit_price, total_price)
SELECT sale_stage.order_id,
       product.product_id,
       sale_stage.quantity,
       sale_stage.unit_price,
       sale_stage.total_price
FROM sale_stage
         JOIN product
              ON product.product_name = sale_stage.product_name
                 AND product.category = sale_stage.category
