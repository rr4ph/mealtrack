from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.src.supermarkets.morrisons import Morrisons
from backend.src.utils.enums import SupermarketType
from backend.src.classes.product import Product

router = APIRouter()

class ProductResponse(BaseModel):
    external_id: str
    name: str
    price: float
    currency: str
    brand: str | None = None
    pack_size: str | None = None
    unit_price: float | None = None
    unit_currency: str | None = None
    unit_name: str | None = None
    in_catalog: bool
    promotions: list[str]
    category: list[str]
    supermarket: str


class ProductCreate(BaseModel):
    external_id: str | None = None
    ingredient_type_id: int | None = None
    name: str
    price: float
    currency: str
    brand: str | None = None
    pack_size: str | None = None
    unit_price: float | None = None
    unit_currency: str | None = None
    unit_name: str | None = None
    supermarket: str

@router.get("/products", response_model=list[ProductResponse])
def get_products(query: str):
    morrisons = Morrisons()

    products = morrisons.get_product(query)

    return [
        ProductResponse(
            external_id=product.external_id,
            name=product.name,
            price=product.price,
            currency=product.currency,
            brand=product.brand,
            pack_size=product.pack_size,
            unit_price=product.unit_price,
            unit_currency=product.unit_currency,
            unit_name=product.unit_name,
            in_catalog=product.in_catalog,
            promotions=product.promotions,
            category=product.category,
            supermarket=product.supermarket.value,
        )
        for product in products
    ]


@router.post("/products", response_model=ProductResponse)
def create_product(product_data: ProductCreate):
    try:
        product = Product(
            external_id=product_data.external_id,
            ingredient_type_id=product_data.ingredient_type_id,
            name=product_data.name,
            price=product_data.price,
            currency=product_data.currency,
            brand=product_data.brand,
            pack_size=product_data.pack_size,
            unit_price=product_data.unit_price,
            unit_currency=product_data.unit_currency,
            unit_name=product_data.unit_name,
            supermarket=SupermarketType(product_data.supermarket),
            in_catalog=True
        )

        product.save_product()

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return ProductResponse(
        external_id=product.external_id,
        name=product.name,
        price=product.price,
        currency=product.currency,
        brand=product.brand,
        pack_size=product.pack_size,
        unit_price=product.unit_price,
        unit_currency=product.unit_currency,
        unit_name=product.unit_name,
        in_catalog=product.in_catalog,
        promotions=product.promotions or [],
        category=product.category or [],
        supermarket=product.supermarket.value,
    )