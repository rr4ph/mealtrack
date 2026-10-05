import pytest

from backend.src.classes.ingredient import Ingredient


def test_save_new_ingredient(db_connection, test_meal, test_ingredient_type):
    ingredient = Ingredient(
        meal_id=test_meal.meal_id,
        ingredient_type_id=test_ingredient_type,
        quantity=200,
        quantity_unit="g",
        connection_choice=db_connection,
    )

    assert ingredient.save_ingredient() is True
    assert ingredient.ingredient_id is not None


def test_update_ingredient(db_connection, test_meal, test_ingredient_type):
    ingredient = Ingredient(
        meal_id=test_meal.meal_id,
        ingredient_type_id=test_ingredient_type,
        quantity=200,
        quantity_unit="g",
        connection_choice=db_connection,
    )
    ingredient.save_ingredient()

    ingredient.quantity = 300
    ingredient.quantity_unit = "g"

    assert ingredient.save_ingredient() is True

    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT quantity, quantity_unit
                FROM ingredients
                WHERE ingredient_id = %s
                """,
                (ingredient.ingredient_id,),
            )
            assert cursor.fetchone() == (300, "g")


def test_get_ingredient_type(db_connection, test_meal, test_ingredient_type):
    ingredient = Ingredient(
        meal_id=test_meal.meal_id,
        ingredient_type_id=test_ingredient_type,
        quantity=1,
        quantity_unit="unit",
        connection_choice=db_connection,
    )

    assert ingredient.get_ingredient_type() == "Tomato"


def test_get_missing_ingredient_type(db_connection, test_meal):
    ingredient = Ingredient(
        meal_id=test_meal.meal_id,
        ingredient_type_id=999,
        quantity=1,
        quantity_unit="unit",
        connection_choice=db_connection,
    )

    with pytest.raises(ValueError, match="Ingredient doesn't have a type."):
        ingredient.get_ingredient_type()


def test_get_meal(db_connection, test_meal):
    ingredient = Ingredient(
        meal_id=test_meal.meal_id,
        ingredient_type_id=1,
        quantity=1,
        quantity_unit="unit",
        connection_choice=db_connection,
    )

    meal = ingredient.get_meal()

    assert meal.meal_id == test_meal.meal_id
    assert meal.user_id == test_meal.user_id
    assert meal.name == "Test Meal"


def test_get_missing_meal(db_connection, test_ingredient_type):
    ingredient = Ingredient(
        meal_id=999,
        ingredient_type_id=test_ingredient_type,
        quantity=1,
        quantity_unit="unit",
        connection_choice=db_connection,
    )

    with pytest.raises(ValueError, match="Ingredient doesn't match any meals."):
        ingredient.get_meal()


def test_remove_ingredient(db_connection, test_meal, test_ingredient_type):
    ingredient = Ingredient(
        meal_id=test_meal.meal_id,
        ingredient_type_id=test_ingredient_type,
        quantity=200,
        quantity_unit="g",
        connection_choice=db_connection,
    )
    ingredient.save_ingredient()

    assert ingredient.remove_ingredient() is True

    with pytest.raises(ValueError, match="Ingredient not found in the meal."):
        ingredient.increase_quantity(10)


def test_remove_missing_ingredient(db_connection, test_meal, test_ingredient_type):
    ingredient = Ingredient(
        meal_id=test_meal.meal_id,
        ingredient_type_id=test_ingredient_type,
        quantity=200,
        quantity_unit="g",
        ingredient_id=999,
        connection_choice=db_connection,
    )

    with pytest.raises(ValueError, match="Ingredient not found."):
        ingredient.remove_ingredient()


def test_increase_quantity(db_connection, test_meal, test_ingredient_type):
    ingredient = Ingredient(
        meal_id=test_meal.meal_id,
        ingredient_type_id=test_ingredient_type,
        quantity=200,
        quantity_unit="g",
        connection_choice=db_connection,
    )
    ingredient.save_ingredient()

    assert ingredient.increase_quantity(50) == 250
    assert ingredient.quantity == 250


def test_decrease_quantity(db_connection, test_meal, test_ingredient_type):
    ingredient = Ingredient(
        meal_id=test_meal.meal_id,
        ingredient_type_id=test_ingredient_type,
        quantity=200,
        quantity_unit="g",
        connection_choice=db_connection,
    )
    ingredient.save_ingredient()

    assert ingredient.decrease_quantity(50) == 150
    assert ingredient.quantity == 150


def test_increase_missing_ingredient(db_connection, test_meal, test_ingredient_type):
    ingredient = Ingredient(
        meal_id=test_meal.meal_id,
        ingredient_type_id=test_ingredient_type,
        quantity=200,
        quantity_unit="g",
        ingredient_id=999,
        connection_choice=db_connection,
    )

    with pytest.raises(ValueError, match="Ingredient not found in the meal."):
        ingredient.increase_quantity(50)


def test_decrease_missing_ingredient(db_connection, test_meal, test_ingredient_type):
    ingredient = Ingredient(
        meal_id=test_meal.meal_id,
        ingredient_type_id=test_ingredient_type,
        quantity=200,
        quantity_unit="g",
        ingredient_id=999,
        connection_choice=db_connection,
    )

    with pytest.raises(ValueError, match="Ingredient not found in the meal."):
        ingredient.decrease_quantity(50)
