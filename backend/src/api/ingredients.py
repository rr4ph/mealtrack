from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.src.classes.ingredient import Ingredient

from backend.src.utils.auth import require_meal_owner

router = APIRouter()


class IngredientResponse(BaseModel):
    ingredient_id: int
    meal_id: int
    ingredient_type_id: int
    quantity: float
    quantity_unit: str


class IngredientCreate(BaseModel):
    ingredient_type_id: int
    quantity: float
    quantity_unit: str


class QuantityUpdateAPI(BaseModel):
    quantity: float


@router.post(
    "/meals/{meal_id}/ingredients", dependencies=[Depends(require_meal_owner)],
    response_model=IngredientResponse
)
def create_ingredient(meal_id: int, ingredient_data: IngredientCreate):
    ingredient = Ingredient(
        meal_id=meal_id,
        ingredient_type_id=ingredient_data.ingredient_type_id,
        quantity=ingredient_data.quantity,
        quantity_unit=ingredient_data.quantity_unit
    )

    ingredient.save_ingredient()

    return IngredientResponse(
        ingredient_id=ingredient.ingredient_id,
        meal_id=ingredient.meal_id,
        ingredient_type_id=ingredient.ingredient_type_id,
        quantity=ingredient.quantity,
        quantity_unit=ingredient.quantity_unit
    )


@router.patch(
    "/meals/{meal_id}/ingredients/{ingredient_id}", dependencies=[Depends(require_meal_owner)],
    response_model=IngredientResponse
)
def update_ingredient(
    meal_id: int,
    ingredient_id: int,
    ingredient_data: IngredientCreate
):
    ingredient = Ingredient(
        meal_id=meal_id,
        ingredient_type_id=ingredient_data.ingredient_type_id,
        quantity=ingredient_data.quantity,
        quantity_unit=ingredient_data.quantity_unit,
        ingredient_id=ingredient_id
    )

    ingredient.save_ingredient()

    return IngredientResponse(
        ingredient_id=ingredient.ingredient_id,
        meal_id=ingredient.meal_id,
        ingredient_type_id=ingredient.ingredient_type_id,
        quantity=ingredient.quantity,
        quantity_unit=ingredient.quantity_unit
    )


@router.post(
    "/meals/{meal_id}/ingredients/{ingredient_id}/increase", dependencies=[Depends(require_meal_owner)]
)
def increase_quantity(
    meal_id: int,
    ingredient_id: int,
    data: QuantityUpdateAPI
):
    ingredient = Ingredient(
        meal_id=meal_id,
        ingredient_type_id=0,
        quantity=0,
        quantity_unit="",
        ingredient_id=ingredient_id
    )

    try:
        quantity = ingredient.increase_quantity(data.quantity)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return {"quantity": quantity}


@router.post(
    "/meals/{meal_id}/ingredients/{ingredient_id}/decrease", dependencies=[Depends(require_meal_owner)]
)
def decrease_quantity(
    meal_id: int,
    ingredient_id: int,
    data: QuantityUpdateAPI
):
    ingredient = Ingredient(
        meal_id=meal_id,
        ingredient_type_id=0,
        quantity=0,
        quantity_unit="",
        ingredient_id=ingredient_id
    )

    try:
        quantity = ingredient.decrease_quantity(data.quantity)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return {"quantity": quantity}


@router.delete(
    "/meals/{meal_id}/ingredients/{ingredient_id}", dependencies=[Depends(require_meal_owner)]
)
def delete_ingredient(meal_id: int, ingredient_id: int):
    ingredient = Ingredient(
        meal_id=meal_id,
        ingredient_type_id=0,
        quantity=0,
        quantity_unit="",
        ingredient_id=ingredient_id
    )

    try:
        ingredient.remove_ingredient()
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return {"message": "Ingredient has been removed."}