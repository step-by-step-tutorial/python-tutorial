CREATE TABLE IF NOT EXISTS app_datawarehouse.house_table (
    listing_key String,
    area Float64,
    room Float64,
    parking Nullable(Bool),
    warehouse Nullable(Bool),
    elevator Nullable(Bool),
    address Nullable(String),
    price Float64,
    price_usd Nullable(Float64),
    price_per_square_meter Nullable(Float64),
    price_usd_per_square_meter Nullable(Float64)
)
ENGINE = MergeTree()
ORDER BY listing_key;
