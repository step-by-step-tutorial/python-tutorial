CREATE SCHEMA IF NOT EXISTS house;

CREATE TABLE IF NOT EXISTS house.house_stage (
    listing_key VARCHAR(64),
    area NUMERIC(12, 4) NOT NULL,
    room NUMERIC(12, 4) NOT NULL,
    parking BOOLEAN,
    warehouse BOOLEAN,
    elevator BOOLEAN,
    address VARCHAR(250),
    price NUMERIC(14, 2) NOT NULL,
    price_usd NUMERIC(14, 2),
    price_per_square_meter NUMERIC(14, 4),
    price_usd_per_square_meter NUMERIC(14, 4)
);
