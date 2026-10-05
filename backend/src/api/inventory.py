from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.src.classes.inventory import Inventory

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

@router.get(
    "/inventory/{inventory_id}/items/{product_id}",
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
    "/inventory/{inventory_id}/items",
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
    "/inventory/{inventory_id}/items/{product_id}/increase"
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
    "/inventory/{inventory_id}/items/{product_id}/decrease"
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

@router.patch(
    "/inventory/{inventory_id}/items/{product_id}"
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
    "/inventory/{inventory_id}/items/{product_id}"
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