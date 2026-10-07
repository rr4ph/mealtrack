from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.database.connections import get_connection
from backend.src.classes.inventory import Inventory

from backend.src.utils.shortages import convert_quantity
from backend.src.utils.auth import require_inventory_owner, require_query_user

router = APIRouter()

class InventoryItemAPI(BaseModel):
    product_id: int
    quantity: float
    quantity_unit: str

class QuantityUpdateAPI(BaseModel):
    quantity: float

class InventoryItemUpdateAPI(BaseModel):
    quantity: float
    quantity_unit: str

class InventoryListItemAPI(BaseModel):
    product_id: int
    name: str
    brand: str | None
    quantity: float
    quantity_unit: str
    ingredient_type_id: int | None = None
    ingredient_type_name: str | None = None

class InventoryListAPI(BaseModel):
    inventory_id: int
    items: list[InventoryListItemAPI]

@router.get("/inventory", dependencies=[Depends(require_query_user)], response_model=InventoryListAPI)
def get_user_inventory(user_id: int):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT inventory_id FROM user_inventories WHERE user_id = %s",
                (user_id,)
            )
            row = cursor.fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Inventory not found.")

            cursor.execute(
                """
                SELECT p.product_id, p.name, p.brand, i.quantity, i.quantity_unit,
                       p.ingredient_type_id, t.name
                FROM inventory_items i
                JOIN products p ON p.product_id = i.product_id
                LEFT JOIN ingredient_types t ON t.ingredient_type_id = p.ingredient_type_id
                WHERE i.inventory_id = %s
                ORDER BY p.name
                """,
                (row[0],)
            )
            items = [
                InventoryListItemAPI(
                    product_id=r[0], name=r[1], brand=r[2],
                    quantity=float(r[3]), quantity_unit=r[4],
                    ingredient_type_id=r[5], ingredient_type_name=r[6]
                )
                for r in cursor.fetchall()
            ]

    return InventoryListAPI(inventory_id=row[0], items=items)

@router.get(
    "/inventory/{inventory_id}/items/{product_id}", dependencies=[Depends(require_inventory_owner)],
    response_model=InventoryItemAPI
)
def get_inventory_item(inventory_id: int, product_id: int):
    inventory = Inventory()
    inventory.inventory_id = inventory_id

    try:
        item = inventory.get_item(product_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return InventoryItemAPI(
        product_id=item.product_id,
        quantity=item.quantity,
        quantity_unit=item.quantity_unit
    )


@router.post(
    "/inventory/{inventory_id}/items", dependencies=[Depends(require_inventory_owner)],
    response_model=InventoryItemAPI
)
def add_inventory_item(
    inventory_id: int,
    item: InventoryItemAPI
):
    inventory = Inventory()
    inventory.inventory_id = inventory_id

    try:
        inventory.add_item(
            product_id=item.product_id,
            quantity=item.quantity,
            quantity_unit=item.quantity_unit
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return item

@router.post(
    "/inventory/{inventory_id}/items/{product_id}/increase", dependencies=[Depends(require_inventory_owner)]
)
def increase_inventory_item(
    inventory_id: int,
    product_id: int,
    data: QuantityUpdateAPI
):
    inventory = Inventory()
    inventory.inventory_id = inventory_id

    try:
        message = inventory.increase_quantity(
            product_id,
            data.quantity
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"message": message}

@router.post(
    "/inventory/{inventory_id}/items/{product_id}/decrease", dependencies=[Depends(require_inventory_owner)]
)
def decrease_inventory_item(
    inventory_id: int,
    product_id: int,
    data: QuantityUpdateAPI
):
    inventory = Inventory()
    inventory.inventory_id = inventory_id

    try:
        message = inventory.decrease_quantity(
            product_id,
            data.quantity
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return {"message": message}

@router.get(
    "/inventory/{inventory_id}/items/{product_id}/convert",
    dependencies=[Depends(require_inventory_owner)],
)
def convert_inventory_item_quantity(
    inventory_id: int,
    product_id: int,
    quantity: float,
    from_unit: str,
    to_unit: str,
):
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT pack_size FROM products WHERE product_id = %s", (product_id,)
            )
            row = cursor.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    return {"quantity": convert_quantity(quantity, from_unit, to_unit, row[0])}


@router.patch(
    "/inventory/{inventory_id}/items/{product_id}", dependencies=[Depends(require_inventory_owner)]
)
def update_inventory_item(
    inventory_id: int,
    product_id: int,
    data: InventoryItemUpdateAPI
):
    inventory = Inventory()
    inventory.inventory_id = inventory_id

    try:
        message = inventory.update_item(
            product_id,
            data.quantity,
            data.quantity_unit
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return {"message": message}

@router.delete(
    "/inventory/{inventory_id}/items/{product_id}", dependencies=[Depends(require_inventory_owner)]
)
def remove_inventory_item(
    inventory_id: int,
    product_id: int
):
    inventory = Inventory()
    inventory.inventory_id = inventory_id

    try:
        message = inventory.remove_item(product_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return {"message": message}