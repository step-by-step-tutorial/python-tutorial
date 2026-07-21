INSERT INTO sale_order (order_id, customer_id, order_date)
SELECT DISTINCT sale_stage.order_id, customer.customer_id, sale_stage.order_date
FROM sale_stage
         JOIN customer
              ON customer.customer_name = sale_stage.customer_name
                 AND customer.country = sale_stage.country
