from dataclasses import dataclass

@dataclass
class Shop:
    address_id: str
    shop_address: str
    shop_name: str
    latitude: float
    longitude: float
    postal_code: str
    distance: float | None = None