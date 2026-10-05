import pytest

from backend.src.utils.ingredient_type_methods import (
    create_ingredient_type,
    merge_ingredient_types,
)


def test_create_ingredient_type(db_connection):
    create_ingredient_type("Cheese", db_connection)

    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM ingredient_types WHERE name = %s",
                ("Cheese",),
            )
            assert cursor.fetchone() == ("Cheese",)


def test_merge_ingredient_types_updates_references(
    db_connection,
    test_user,
):
    from backend.src.classes.meal import Meal
    from backend.src.classes.ingredient import Ingredient
    from backend.src.classes.product import Product
    from backend.src.utils.enums import SupermarketType

    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO ingredient_types(name) VALUES (%s) RETURNING ingredient_type_id",
                ("Tomato",),
            )
            kept_id = cursor.fetchone()[0]

            cursor.execute(
                "INSERT INTO ingredient_types(name) VALUES (%s) RETURNING ingredient_type_id",
                ("Tomatoes",),
            )
            deleted_id = cursor.fetchone()[0]

    meal = Meal(
        test_user.user_id,
        "Pasta",
        2,
        "portions",
        connection_choice=db_connection,
    )
    meal.save_meal()

    ingredient = Ingredient(
        meal.meal_id,
        deleted_id,
        200,
        "g",
        connection_choice=db_connection,
    )
    ingredient.save_ingredient()

    product = Product(
        "Tomatoes",
        1.50,
        "GBP",
        SupermarketType.TESCO,
        ingredient_type_id=deleted_id,
        connection_choice=db_connection,
    )
    product.save_product()

    assert merge_ingredient_types(kept_id, deleted_id, db_connection) is True

    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT ingredient_type_id FROM ingredients WHERE ingredient_id = %s",
                (ingredient.ingredient_id,),
            )
            assert cursor.fetchone()[0] == kept_id

            cursor.execute(
                "SELECT ingredient_type_id FROM products WHERE product_id = %s",
                (product.product_id,),
            )
            assert cursor.fetchone()[0] == kept_id

            cursor.execute(
                "SELECT ingredient_type_id FROM ingredient_types WHERE ingredient_type_id = %s",
                (deleted_id,),
            )
            assert cursor.fetchone() is None
