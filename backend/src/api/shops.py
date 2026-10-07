import logging

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.database.connections import get_connection
from backend.src.supermarkets.morrisons import Morrisons
from backend.src.supermarkets.tesco import Tesco
from backend.src.supermarkets.sainsburys import Sainsburys
from backend.src.utils.geography import get_coordinates, get_shop_distances

logger = logging.getLogger(__name__)
router = APIRouter()


class ShopResponse(BaseModel):
    address_id: str
    shop_name: str
    shop_address: str
    supermarket: str
    distance: float | None = None
    latitude: float
    longitude: float


@router.get("/shops", response_model=list[ShopResponse])
def get_shops_for_user(user_id: int = Query(...)):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT postcode FROM users WHERE user_id = %s",
                (user_id,)
            )
            row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail="User not found.")

    postcode = row[0]
    if not postcode:
        raise HTTPException(
            status_code=400,
            detail="User postcode not set. Update your profile with a postcode to find nearby shops."
        )

    try:
        user_lat, user_lon = get_coordinates(postcode)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    providers = [
        ("morrisons", Morrisons()),
        ("tesco", Tesco()),
        ("sainsburys", Sainsburys()),
    ]

    all_shops = []
    for supermarket_name, provider in providers:
        try:
            shops = provider.get_shops(postcode)
            for shop in shops:
                shop.supermarket = supermarket_name
            all_shops.extend(shops)
        except Exception as error:
            logger.warning("%s shops unavailable: %s: %s", supermarket_name, type(error).__name__, error)

    if not all_shops:
        raise HTTPException(
            status_code=502,
            detail="Could not retrieve shops from any supermarket."
        )

    get_shop_distances(all_shops, user_lat, user_lon)

    return [
        ShopResponse(
            address_id=shop.address_id,
            shop_name=shop.shop_name,
            shop_address=shop.shop_address,
            supermarket=shop.supermarket,
            distance=shop.distance,
            latitude=shop.latitude,
            longitude=shop.longitude,
        )
        for shop in all_shops
    ]
