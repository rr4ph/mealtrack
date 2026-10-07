from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.src.classes.meal import Meal

from backend.src.utils.auth import current_user_id, require_meal_owner, require_query_user

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
def create_meal(meal_data: MealCreate, auth_id: int = Depends(current_user_id)):
    if meal_data.user_id != auth_id:
        raise HTTPException(status_code=403, detail="Forbidden.")
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


@router.patch("/meals/{meal_id}", dependencies=[Depends(require_meal_owner)], response_model=MealResponse)
def update_meal(meal_id: int, meal_data: MealCreate, auth_id: int = Depends(current_user_id)):
    if meal_data.user_id != auth_id:
        raise HTTPException(status_code=403, detail="Forbidden.")
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
    "/meals/{meal_id}/ingredients", dependencies=[Depends(require_meal_owner), Depends(require_query_user)],
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
    "/meals/{meal_id}/ingredients/{ingredient_id}", dependencies=[Depends(require_meal_owner), Depends(require_query_user)],
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


@router.delete("/meals/{meal_id}", dependencies=[Depends(require_meal_owner), Depends(require_query_user)])
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

@router.get("/meals", dependencies=[Depends(require_query_user)], response_model=list[MealResponse])
def get_meals(user_id: int):
    meal = Meal(
        user_id=user_id,
        name="",
        portion=0,
        portion_unit=""
    )

    meals = meal.get_meals()

    return [
        MealResponse(
            meal_id=meal.meal_id,
            user_id=meal.user_id,
            name=meal.name,
            portion=meal.portion,
            portion_unit=meal.portion_unit
        )
        for meal in meals
    ]