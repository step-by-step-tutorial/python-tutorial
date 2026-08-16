from dataclasses import dataclass


@dataclass(frozen=True)
class HouseAttribute:
    area_raw: str = "Area"
    room_raw: str = "Room"
    parking_raw: str = "Parking"
    warehouse_raw: str = "Warehouse"
    elevator_raw: str = "Elevator"
    address_raw: str = "Address"
    price_raw: str = "Price"
    price_usd_raw: str = "Price(USD)"
    area: str = "area"
    room: str = "room"
    parking: str = "parking"
    warehouse: str = "warehouse"
    elevator: str = "elevator"
    address: str = "address"
    price: str = "price"
    price_usd: str = "price_usd"
    listing_key: str = "listing_key"
    price_per_square_meter: str = "price_per_square_meter"
    price_usd_per_square_meter: str = "price_usd_per_square_meter"

    def __getattr__(self, item: str) -> str:
        lowered = item.lower()
        if hasattr(self, lowered):
            return getattr(self, lowered)
        raise AttributeError(item)


HOUSE_ATTRIBUTE = HouseAttribute()
