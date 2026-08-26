from data_platform.analyzers.aggregate_model import AggregateSpecification
from data_platform.analyzers.analyzer_chain import AnalyzerChain
from data_platform.analyzers.analyzer_impl import GroupAggregateAnalyzer
from data_platform.cleaners.cleaner_impl import (
    BooleanColumnCleaner,
    CleanerChain,
    DropDuplicatesCleaner,
    NumericColumnCleaner,
    StripColumnCleaner,
    ToDatetimeCleaner,
)
from data_platform.config.keys import Key
from data_platform.domain.house.attribute import attribute
from data_platform.domain.house.spark_schema import build_schema
from data_platform.ingestion.csv_file_ingestor import CsvFileIngestor
from data_platform.model.dataframe_model import DataFrameModel
from data_platform.model.dataset import Dataset
from data_platform.model.pipeline_flow import PipelineFlow
from data_platform.registry.endpoint_registry import endpoint_registry
from data_platform.repository.data_exposer import DataExposer
from data_platform.repository.inmemory_database_repository import InmemoryDataframeRepository
from data_platform.repository.inmemory_datalake_repository import DataLakeRepository
from data_platform.repository.inmemory_warehouse_repository import InmemoryWarehouseRepository
from data_platform.validators.validator_chain import ValidatorChain
from data_platform.validators.validator_impl import (
    NotNullValidator,
    PositiveValidator,
    RequiredColumnsValidator,
)


numeric_columns = (
    attribute.latitude, attribute.longitude, attribute.construction_year,
    attribute.renovation_year, attribute.area_sqm, attribute.living_area_sqm,
    attribute.land_area_sqm, attribute.room_count, attribute.bedroom_count,
    attribute.bathroom_count, attribute.toilet_count, attribute.floor_number,
    attribute.total_floors, attribute.resident_count, attribute.adult_count,
    attribute.child_count, attribute.purchase_price, attribute.price_per_sqm,
    attribute.total_price, attribute.estimated_market_value, attribute.monthly_rent,
    attribute.monthly_service_cost, attribute.annual_property_tax, attribute.balcony_area_sqm,
    attribute.garden_area_sqm, attribute.garage_capacity, attribute.parking_spaces,
    attribute.basement_area_sqm, attribute.annual_energy_consumption_kwh,
    attribute.internet_speed_mbps, attribute.distance_to_city_center_km,
    attribute.distance_to_school_km, attribute.distance_to_supermarket_km,
    attribute.distance_to_public_transport_km,
)
boolean_columns = (
    attribute.owner_occupied, attribute.has_balcony, attribute.has_garden,
    attribute.has_garage, attribute.has_basement, attribute.has_elevator,
    attribute.has_storage_room, attribute.has_fireplace, attribute.has_swimming_pool,
    attribute.has_solar_panels, attribute.furnished, attribute.internet_available,
)
date_columns = (attribute.purchase_date, attribute.created_at, attribute.updated_at)
text_columns = (
    attribute.property_type, attribute.address, attribute.street, attribute.house_number,
    attribute.postal_code, attribute.city, attribute.state, attribute.country,
    attribute.owner_id, attribute.owner_name, attribute.owner_type,
    attribute.occupancy_status, attribute.ownership_status, attribute.currency,
    attribute.heating_type, attribute.energy_source, attribute.energy_efficiency_class,
    attribute.condition,
)


house_dataset = Dataset(
    name="house",
    dataframe=DataFrameModel(
        schema=build_schema(),
        required_columns=frozenset(attribute.columns),
    ),
    audit=endpoint_registry.get_item("audit"),
    endpoints={
        Key.HOUSE_CSV_FILE: endpoint_registry.get_item(Key.HOUSE_CSV_FILE),
        Key.HOUSE_KAFKA_CONSUMER: endpoint_registry.get_item(Key.HOUSE_KAFKA_CONSUMER),
        Key.HOUSE_KAFKA_PRODUCER: endpoint_registry.get_item(Key.HOUSE_KAFKA_PRODUCER),
        Key.HOUSE_DATA_LAKE: endpoint_registry.get_item(Key.HOUSE_DATA_LAKE),
        Key.HOUSE_DATABASE: endpoint_registry.get_item(Key.HOUSE_DATABASE),
        Key.HOUSE_WAREHOUSE: endpoint_registry.get_item(Key.HOUSE_WAREHOUSE),
    },
    flow=PipelineFlow(
        repository=DataLakeRepository(endpoint_registry.get_item(Key.HOUSE_DATA_LAKE)),
        ingestors=(CsvFileIngestor(endpoint_registry.get_item(Key.HOUSE_CSV_FILE)),),
        cleaners=CleanerChain(
            tuple(NumericColumnCleaner(column) for column in numeric_columns)
            + tuple(BooleanColumnCleaner(column) for column in boolean_columns)
            + tuple(ToDatetimeCleaner(column) for column in date_columns)
            + tuple(StripColumnCleaner(column) for column in text_columns)
            + (DropDuplicatesCleaner(attribute.property_id),)
        ),
        validators=ValidatorChain((
            RequiredColumnsValidator(attribute.columns),
            NotNullValidator(attribute.property_id),
            NotNullValidator(attribute.area_sqm),
            NotNullValidator(attribute.total_price),
            PositiveValidator(attribute.area_sqm),
            PositiveValidator(attribute.total_price),
        )),
        enrichers=(),
        exposers=(
            DataExposer((InmemoryDataframeRepository(endpoint_registry.get_item(Key.HOUSE_DATABASE)).overwrite,)),
            DataExposer((InmemoryWarehouseRepository(endpoint_registry.get_item(Key.HOUSE_WAREHOUSE)).overwrite,)),
        ),
        analyzers=AnalyzerChain((
            GroupAggregateAnalyzer(
                "average_price_by_city",
                AggregateSpecification(attribute.city, attribute.total_price, "mean", "average_price"),
            ),
            GroupAggregateAnalyzer(
                "average_price_per_square_meter_by_property_type",
                AggregateSpecification(attribute.property_type, attribute.price_per_sqm, "mean", "average_price_per_sqm"),
            ),
        )),
    ),
)
