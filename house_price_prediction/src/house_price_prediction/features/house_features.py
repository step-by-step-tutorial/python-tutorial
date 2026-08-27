import logging

import pandas as pd

from house_price_prediction.utils.collection_utils import check_equal

logger = logging.getLogger(__name__)

NUMERIC_FEATURES = (
    "latitude",
    "longitude",
    "construction_year",
    "renovation_year",
    "area_sqm",
    "living_area_sqm",
    "land_area_sqm",
    "room_count",
    "bedroom_count",
    "bathroom_count",
    "toilet_count",
    "floor_number",
    "total_floors",
    "balcony_area_sqm",
    "garden_area_sqm",
    "garage_capacity",
    "parking_spaces",
    "basement_area_sqm",
    "annual_energy_consumption_kwh",
    "internet_speed_mbps",
    "distance_to_city_center_km",
    "distance_to_school_km",
    "distance_to_supermarket_km",
    "distance_to_public_transport_km",
)

BOOLEAN_FEATURES = (
    "owner_occupied",
    "has_balcony",
    "has_garden",
    "has_garage",
    "has_basement",
    "has_elevator",
    "has_storage_room",
    "has_fireplace",
    "has_swimming_pool",
    "has_solar_panels",
    "furnished",
    "internet_available",
)

CATEGORICAL_FEATURES = (
    "property_type",
    "city",
    "state",
    "country",
    "owner_type",
    "occupancy_status",
    "ownership_status",
    "currency",
    "heating_type",
    "energy_source",
    "energy_efficiency_class",
    "condition",
)

FEATURE_COLUMNS = NUMERIC_FEATURES + BOOLEAN_FEATURES + CATEGORICAL_FEATURES


class HouseFeatureBuilder:
    def build(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        check_equal(FEATURE_COLUMNS, dataframe.columns)

        features = dataframe.loc[:, FEATURE_COLUMNS].copy()
        for column in BOOLEAN_FEATURES:
            features[column] = features[column].map({True: 1, False: 0, "True": 1, "False": 0})

        logger.info(f"Built house features: rows={len(features)} columns={len(features.columns)}")
        return features
