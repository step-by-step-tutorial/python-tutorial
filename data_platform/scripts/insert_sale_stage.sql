INSERT INTO public.sale_stage (
    pipeline_id,
    order_id,
    customer_id,
    product_id,
    quantity,
    unit_price,
    total_price,
    event_time
)
VALUES (
    :pipeline_id,
    :order_id,
    :customer_id,
    :product_id,
    :quantity,
    :unit_price,
    :total_price,
    :event_time
)
ON CONFLICT (pipeline_id, order_id, product_id)
DO UPDATE
    SET
        customer_id = EXCLUDED.customer_id,
        quantity = EXCLUDED.quantity,
        unit_price = EXCLUDED.unit_price,
        total_price = EXCLUDED.total_price,
        event_time = EXCLUDED.event_time;