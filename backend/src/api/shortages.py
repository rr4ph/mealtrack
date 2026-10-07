from fastapi import APIRouter, Depends
from pydantic import BaseModel

from backend.database.connections import get_connection
from backend.src.utils.auth import require_query_user
from backend.src.utils.shortages import calculate_shortages

router = APIRouter()


class ShortageAPI(BaseModel):
    meal_id: int
    meal_name: str
    ingredient_type_id: int
    ingredient_type_name: str
    required_quantity: float
    available_quantity: float
    missing_quantity: float
    quantity_unit: str
    incompatible_units: list[str]


@router.get("/shortages", dependencies=[Depends(require_query_user)], response_model=list[ShortageAPI])
def get_shortages(user_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT m.meal_id, m.name, t.ingredient_type_id, t.name,
                       i.quantity, i.quantity_unit
                FROM meals m
                JOIN ingredients i ON i.meal_id = m.meal_id
                JOIN ingredient_types t ON t.ingredient_type_id = i.ingredient_type_id
                WHERE m.user_id = %s
                ORDER BY m.name, t.name
                """,
                (user_id,)
            )
            ingredients = cursor.fetchall()

            cursor.execute(
                """
                SELECT p.ingredient_type_id, ii.quantity, ii.quantity_unit, p.pack_size
                FROM user_inventories inv
                JOIN inventory_items ii ON ii.inventory_id = inv.inventory_id
                JOIN products p ON p.product_id = ii.product_id
                WHERE inv.user_id = %s AND p.ingredient_type_id IS NOT NULL
                """,
                (user_id,)
            )
            stock = cursor.fetchall()

    return calculate_shortages(ingredients, stock)
