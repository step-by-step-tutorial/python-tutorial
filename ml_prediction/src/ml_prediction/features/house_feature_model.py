from ml_prediction.features.feature_model import FeatureModel


class HouseFeatureModel(FeatureModel):
    numeric_features = (
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

    boolean_features = (
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

    categorical_features = (
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

    def get_numeric_features(self) -> tuple[str, ...]:
        return self.numeric_features

    def get_boolean_features(self) -> tuple[str, ...]:
        return self.boolean_features

    def get_categorical_features(self) -> tuple[str, ...]:
        return self.categorical_features
