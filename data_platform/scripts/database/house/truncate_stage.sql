CREATE SCHEMA IF NOT EXISTS house;
DROP TABLE IF EXISTS house.house_stage;
CREATE TABLE house.house_stage (
    listing_key VARCHAR(64),
    area NUMERIC(20, 4) NOT NULL,
    room NUMERIC(20, 4) NOT NULL,
    parking BOOLEAN,
    warehouse BOOLEAN,
    elevator BOOLEAN,
    address VARCHAR(250),
    price NUMERIC(20, 2) NOT NULL,
    price_usd NUMERIC(20, 2),
    price_per_square_meter NUMERIC(20, 4),
    price_usd_per_square_meter NUMERIC(20, 4)
);
TRUNCATE TABLE house.house_stage;
