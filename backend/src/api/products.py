import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.src.supermarkets.morrisons import Morrisons
from backend.src.supermarkets.tesco import Tesco
from backend.src.supermarkets.sainsburys import Sainsburys
from backend.src.utils.enums import SupermarketType
from backend.src.classes.product import Product
from backend.src.utils.auth import current_user_id
from fastapi import Depends

logger = logging.getLogger(__name__)
router = APIRouter()


class ProductResponse(BaseModel):
    product_id: int
    external_id: str
    name: str
    price: float
    currency: str
    brand: str | None = None
    pack_size: str | None = None
    unit_price: float | None = None
    unit_currency: str | None = None
    unit_name: str | None = None
    ingredient_type_id: int | None = None
    ingredient_type_name: str | None = None
    in_catalog: bool
    promotions: list[str]
    category: list[str]
    supermarket: str
    last_price_update_at: str | None = None


class ProductTypeUpdate(BaseModel):
    ingredient_type_id: int | None = None


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
def get_products(query: str, supermarket: str = "all"):
    supermarkets = {
        "morrisons": Morrisons,
        "tesco": Tesco,
        "sainsburys": Sainsburys,
    }

    if supermarket == "all":
        providers = supermarkets.items()
    elif supermarket in supermarkets:
        providers = [(supermarket, supermarkets[supermarket])]
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown supermarket: {supermarket}"
        )

    products = []

    for name, provider_class in providers:
        try:
            provider = provider_class()
            products.extend(provider.get_product(query))

        except Exception as error:
            logger.warning("%s products unavailable: %s: %s", name, type(error).__name__, error)
            if supermarket != "all":
                raise HTTPException(
                    status_code=502,
                    detail=f"{name} supermarket service is unavailable"
                ) from error

    result = []
    for product in products:
        db_product = _get_or_create_product(product)
        result.append(ProductResponse(
            product_id=db_product.product_id,
            external_id=product.external_id,
            name=product.name,
            price=product.price,
            currency=product.currency,
            brand=product.brand,
            pack_size=product.pack_size,
            unit_price=product.unit_price,
            unit_currency=product.unit_currency,
            unit_name=product.unit_name,
            ingredient_type_id=db_product.ingredient_type_id,
            ingredient_type_name=_type_name(db_product.ingredient_type_id),
            in_catalog=product.in_catalog,
            promotions=product.promotions or [],
            category=product.category or [],
            supermarket=product.supermarket.value,
            last_price_update_at=db_product.last_price_update_at.isoformat() if db_product.last_price_update_at else None,
        ))
    return result

def _get_or_create_product(product):
    from backend.database.connections import get_connection
    with get_connection() as connection:
        with connection.cursor() as cursor:
            if product.external_id:
                cursor.execute(
                    "SELECT product_id, ingredient_type_id FROM products WHERE external_id = %s",
                    (product.external_id,)
                )
                row = cursor.fetchone()
                if row:
                    p = Product(
                        product_id=row[0],
                        ingredient_type_id=row[1],
                        category=product.category,
                        external_id=product.external_id,
                        name=product.name,
                        price=product.price,
                        currency=product.currency,
                        brand=product.brand,
                        pack_size=product.pack_size,
                        unit_price=product.unit_price,
                        unit_currency=product.unit_currency,
                        unit_name=product.unit_name,
                        supermarket=product.supermarket,
                        in_catalog=True
                    )
                    if p.ingredient_type_id is None:
                        p.auto_assign_ingredient_type()
                        if p.ingredient_type_id is not None:
                            cursor.execute(
                                "UPDATE products SET ingredient_type_id = %s WHERE product_id = %s",
                                (p.ingredient_type_id, p.product_id)
                            )
                    return p
    
    p = Product(
        external_id=product.external_id,
        name=product.name,
        price=product.price,
        currency=product.currency,
        brand=product.brand,
        pack_size=product.pack_size,
        unit_price=product.unit_price,
        unit_currency=product.unit_currency,
        unit_name=product.unit_name,
        supermarket=product.supermarket,
        in_catalog=True,
        category=product.category
    )
    p.auto_assign_ingredient_type()
    p.save_product()
    return p


def _type_name(ingredient_type_id):
    if ingredient_type_id is None:
        return None
    from backend.database.connections import get_connection
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM ingredient_types WHERE ingredient_type_id = %s",
                (ingredient_type_id,)
            )
            row = cursor.fetchone()
    return row[0] if row else None


@router.patch("/products/{product_id}/ingredient-type", dependencies=[Depends(current_user_id)])
def update_product_ingredient_type(product_id: int, data: ProductTypeUpdate):
    from backend.database.connections import get_connection
    if data.ingredient_type_id is not None and _type_name(data.ingredient_type_id) is None:
        raise HTTPException(status_code=404, detail="Ingredient type not found.")
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE products SET ingredient_type_id = %s WHERE product_id = %s",
                (data.ingredient_type_id, product_id)
            )
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Product not found.")
    return {"ingredient_type_id": data.ingredient_type_id}


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
        product.auto_assign_ingredient_type()
        product.save_product()

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    return ProductResponse(
        product_id=product.product_id,
        external_id=product.external_id,
        name=product.name,
        price=product.price,
        currency=product.currency,
        brand=product.brand,
        pack_size=product.pack_size,
        unit_price=product.unit_price,
        unit_currency=product.unit_currency,
        unit_name=product.unit_name,
        ingredient_type_id=product.ingredient_type_id,
        ingredient_type_name=_type_name(product.ingredient_type_id),
        in_catalog=product.in_catalog,
        promotions=product.promotions or [],
        category=product.category or [],
        supermarket=product.supermarket.value,
        last_price_update_at=product.last_price_update_at.isoformat() if product.last_price_update_at else None,
    )
