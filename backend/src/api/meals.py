from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.src.classes.meal import Meal

router = APIRouter()


class MealResponse(BaseModel):
    meal_id: int
    user_id: int
    name: str
    portion: float
    portion_unit: str


class MealCreate(BaseModel):
    user_id: int
    name: str
    portion: float
    portion_unit: str


class IngredientResponse(BaseModel):
    ingredient_id: int
    meal_id: int
    ingredient_type_id: int
    quantity: float
    quantity_unit: str


@router.post("/meals", response_model=MealResponse)
def create_meal(meal_data: MealCreate):
    meal = Meal(
        user_id=meal_data.user_id,
        name=meal_data.name,
        portion=meal_data.portion,
        portion_unit=meal_data.portion_unit
    )

    meal.save_meal()

    return MealResponse(
        meal_id=meal.meal_id,
        user_id=meal.user_id,
        name=meal.name,
        portion=meal.portion,
        portion_unit=meal.portion_unit
    )


@router.patch("/meals/{meal_id}", response_model=MealResponse)
def update_meal(meal_id: int, meal_data: MealCreate):
    meal = Meal(
        user_id=meal_data.user_id,
        name=meal_data.name,
        portion=meal_data.portion,
        portion_unit=meal_data.portion_unit,
        meal_id=meal_id
    )

    meal.save_meal()

    return MealResponse(
        meal_id=meal.meal_id,
        user_id=meal.user_id,
        name=meal.name,
        portion=meal.portion,
        portion_unit=meal.portion_unit
    )


@router.get(
    "/meals/{meal_id}/ingredients",
    response_model=list[IngredientResponse]
)
def get_ingredients(meal_id: int, user_id: int):
    meal = Meal(
        user_id=user_id,
        name="",
        portion=0,
        portion_unit="",
        meal_id=meal_id
    )

    ingredients = meal.get_ingredients()

    return [
        IngredientResponse(
            ingredient_id=ingredient.ingredient_id,
            meal_id=ingredient.meal_id,
            ingredient_type_id=ingredient.ingredient_type_id,
            quantity=ingredient.quantity,
            quantity_unit=ingredient.quantity_unit
        )
        for ingredient in ingredients
    ]


@router.get(
    "/meals/{meal_id}/ingredients/{ingredient_id}",
    response_model=IngredientResponse
)
def get_ingredient(
    meal_id: int,
    ingredient_id: int,
    user_id: int
):
    meal = Meal(
        user_id=user_id,
        name="",
        portion=0,
        portion_unit="",
        meal_id=meal_id
    )

    try:
        ingredient = meal.get_ingredient(ingredient_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return IngredientResponse(
        ingredient_id=ingredient.ingredient_id,
        meal_id=ingredient.meal_id,
        ingredient_type_id=ingredient.ingredient_type_id,
        quantity=ingredient.quantity,
        quantity_unit=ingredient.quantity_unit
    )


@router.delete("/meals/{meal_id}")
def delete_meal(meal_id: int, user_id: int):
    meal = Meal(
        user_id=user_id,
        name="",
        portion=0,
        portion_unit="",
        meal_id=meal_id
    )

    try:
        meal.remove_meal()
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return {"message": "Meal has been removed."}