import pytest

from backend.src.classes.meal import Meal
from backend.src.classes.ingredient import Ingredient


def test_save_new_meal(db_connection, test_user):
    meal = Meal(
        user_id=test_user.user_id,
        name="Pasta",
        portion=4,
        portion_unit="portions",
        connection_choice=db_connection,
    )

    assert meal.save_meal() is True
    assert meal.meal_id is not None


def test_update_meal(db_connection, test_user):
    meal = Meal(
        user_id=test_user.user_id,
        name="Pasta",
        portion=2,
        portion_unit="portions",
        connection_choice=db_connection,
    )
    meal.save_meal()

    meal.name = "Updated Pasta"
    meal.portion = 3

    assert meal.save_meal() is True

    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT name, portion
                FROM meals
                WHERE meal_id = %s
                """,
                (meal.meal_id,),
            )
            assert cursor.fetchone() == ("Updated Pasta", 3)


def test_get_ingredients(db_connection, test_meal, test_ingredient_type):
    first = Ingredient(
        test_meal.meal_id,
        test_ingredient_type,
        200,
        "g",
        connection_choice=db_connection,
    )
    second = Ingredient(
        test_meal.meal_id,
        test_ingredient_type,
        2,
        "unit",
        connection_choice=db_connection,
    )
    first.save_ingredient()
    second.save_ingredient()

    ingredients = test_meal.get_ingredients()

    assert len(ingredients) == 2
    assert all(isinstance(item, Ingredient) for item in ingredients)
    assert {item.ingredient_id for item in ingredients} == {
        first.ingredient_id,
        second.ingredient_id,
    }


def test_get_ingredient(db_connection, test_meal, test_ingredient_type):
    ingredient = Ingredient(
        test_meal.meal_id,
        test_ingredient_type,
        200,
        "g",
        connection_choice=db_connection,
    )
    ingredient.save_ingredient()

    result = test_meal.get_ingredient(ingredient.ingredient_id)

    assert result.ingredient_id == ingredient.ingredient_id
    assert result.meal_id == test_meal.meal_id
    assert result.quantity == 200


def test_get_missing_ingredient(db_connection, test_meal):
    with pytest.raises(ValueError, match="No ingredient with this ID."):
        test_meal.get_ingredient(999)


def test_remove_meal(db_connection, test_meal):
    meal_id = test_meal.meal_id

    assert test_meal.remove_meal() is True

    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT meal_id FROM meals WHERE meal_id = %s",
                (meal_id,),
            )
            assert cursor.fetchone() is None


def test_remove_missing_meal(db_connection, test_user):
    meal = Meal(
        user_id=test_user.user_id,
        name="Missing",
        portion=1,
        portion_unit="portion",
        meal_id=999,
        connection_choice=db_connection,
    )

    with pytest.raises(ValueError, match="Meal not found."):
        meal.remove_meal()
