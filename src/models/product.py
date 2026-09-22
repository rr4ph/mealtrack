from dataclasses import dataclass

@dataclass
class Product:
    external_id: str | None
    name: str
    price: float
    currency: str
    brand: str | None
    pack_size: str | None
    unit_price: float | None
    unit_currency: str | None
    unit_name: str | None
    in_catalog: bool
    promotions: list[str]
    category: list[str] | None
    supermarket: str
