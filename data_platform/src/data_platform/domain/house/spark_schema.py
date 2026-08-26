from pyspark.sql.types import BooleanType, DateType, DoubleType, IntegerType, StringType, StructField, StructType, TimestampType

from data_platform.domain.house.attribute import attribute


_STRING_COLUMNS = {attribute.property_id, attribute.property_type, attribute.address, attribute.street, attribute.house_number, attribute.postal_code, attribute.city, attribute.state, attribute.country, attribute.owner_id, attribute.owner_name, attribute.owner_type, attribute.occupancy_status, attribute.ownership_status, attribute.currency, attribute.heating_type, attribute.energy_source, attribute.energy_efficiency_class, attribute.condition}
_DOUBLE_COLUMNS = {attribute.latitude, attribute.longitude, attribute.area_sqm, attribute.living_area_sqm, attribute.land_area_sqm, attribute.purchase_price, attribute.price_per_sqm, attribute.total_price, attribute.estimated_market_value, attribute.monthly_rent, attribute.monthly_service_cost, attribute.annual_property_tax, attribute.balcony_area_sqm, attribute.garden_area_sqm, attribute.basement_area_sqm, attribute.annual_energy_consumption_kwh, attribute.distance_to_city_center_km, attribute.distance_to_school_km, attribute.distance_to_supermarket_km, attribute.distance_to_public_transport_km}
_INTEGER_COLUMNS = {attribute.construction_year, attribute.renovation_year, attribute.room_count, attribute.bedroom_count, attribute.bathroom_count, attribute.toilet_count, attribute.floor_number, attribute.total_floors, attribute.resident_count, attribute.adult_count, attribute.child_count, attribute.garage_capacity, attribute.parking_spaces, attribute.internet_speed_mbps}
_BOOLEAN_COLUMNS = {attribute.owner_occupied, attribute.has_balcony, attribute.has_garden, attribute.has_garage, attribute.has_basement, attribute.has_elevator, attribute.has_storage_room, attribute.has_fireplace, attribute.has_swimming_pool, attribute.has_solar_panels, attribute.furnished, attribute.internet_available}


HOUSE_SCHEMA = StructType([
    StructField(column, StringType() if column in _STRING_COLUMNS else DoubleType() if column in _DOUBLE_COLUMNS else IntegerType() if column in _INTEGER_COLUMNS else BooleanType() if column in _BOOLEAN_COLUMNS else DateType() if column == attribute.purchase_date else TimestampType(), nullable=True)
    for column in attribute.columns
])
