import pytest
from backend.src.classes.inventory import Inventory
from backend.src.classes.user import User
from backend.database.connections import get_connection

@pytest.fixture
def test_user():
    user = User(
        "test", "testpassword", connection_choice=lambda: get_connection("mealtrack_test")
    )

    user.save_user()
    yield user

    with user.connection_choice() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
            DELETE FROM users WHERE user_id = %s
            """,
            (
                user.user_id,
            ))


@pytest.fixture
def test_product():
    with get_connection("mealtrack_test") as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO ingredient_types(name)
                VALUES (%s)
                RETURNING ingredient_type_id
                """,
                ("Test Ingredient",)
            )

            ingredient_type_id = cursor.fetchone()[0]

            cursor.execute(
                """
                INSERT INTO products(
                    ingredient_type_id,
                    name,
                    price,
                    currency,
                    supermarket,
                    last_price_update_at
                )
                VALUES (%s, %s, %s, %s, %s, NOW())
                RETURNING product_id
                """,
                (
                    ingredient_type_id,
                    "Test Product",
                    1.99,
                    "GBP",
                    "Test Supermarket",
                )
            )

            product_id = cursor.fetchone()[0]

    yield product_id

    with get_connection("mealtrack_test") as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                TRUNCATE TABLE
                    ingredients,
                    meals,
                    inventory_items,
                    products,
                    ingredient_types,
                    user_inventories,
                    users
                RESTART IDENTITY CASCADE
            """)

def test_user_creation(test_user):
    assert test_user.user_id is not None
    assert test_user.inventory.inventory_id is not None

def test_add_item(test_user, test_product):
    result = test_user.inventory.add_item(
        test_product,
        200,
        "mg"
    )

    assert result == "Product has been added successfully."

    item = test_user.inventory.get_item(test_product)

    assert item[1] == test_product
    assert item[2] == test_user.inventory.inventory_id
    assert item[3] == 200
    assert item[4] == "mg"

def test_add_duplicate_item(test_user, test_product):
    test_user.inventory.add_item(test_product, 200, "mg")

    with pytest.raises(ValueError, match="Item already exists."):
        test_user.inventory.add_item(test_product, 100, "mg")

def test_increase_quantity(test_user, test_product):
    test_user.inventory.add_item(test_product, 200, "mg")

    result = test_user.inventory.increase_quantity(test_product, 50)

    assert result == "Product is now 250 mg."

def test_increase_missing_item(test_user, test_product):
    with pytest.raises(ValueError, match="Item not found in inventory."):
        test_user.inventory.increase_quantity(test_product, 50)

def test_decrease_quantity(test_user, test_product):
    test_user.inventory.add_item(test_product, 200, "mg")

    result = test_user.inventory.decrease_quantity(test_product, 50)

    assert result == "Product is now 150 mg."

def test_decrease_missing_item(test_user, test_product):
    with pytest.raises(ValueError, match="Item not found in inventory."):
        test_user.inventory.decrease_quantity(test_product, 50)

def test_decrease_below_zero(test_user, test_product):
    test_user.inventory.add_item(test_product, 200, "mg")

    with pytest.raises(
        ValueError,
        match="You don't have enough of this Product."
    ):
        test_user.inventory.decrease_quantity(test_product, 300)

def test_update_item(test_user, test_product):
    test_user.inventory.add_item(test_product, 200, "mg")

    result = test_user.inventory.update_item(test_product, 500, "g")

    assert result == "Product is now 500 g."

    item = test_user.inventory.get_item(test_product)

    assert item[3] == 500
    assert item[4] == "g"

def test_update_missing_item(test_user, test_product):
    with pytest.raises(ValueError, match="Item not found in inventory."):
        test_user.inventory.update_item(test_product, 500, "g")

def test_remove_item(test_user, test_product):
    test_user.inventory.add_item(test_product, 200, "mg")

    result = test_user.inventory.remove_item(test_product)

    assert result == "Item has been removed."

    with pytest.raises(ValueError, match="Item not found in inventory."):
        test_user.inventory.get_item(test_product)

def test_remove_missing_item(test_user, test_product):
    with pytest.raises(ValueError, match="Item not found in inventory."):
        test_user.inventory.remove_item(test_product)

def test_get_item(test_user, test_product):
    test_user.inventory.add_item(test_product, 200, "mg")

    result = test_user.inventory.get_item(test_product)

    assert result[1] == test_product
    assert result[2] == test_user.inventory.inventory_id
    assert result[3] == 200
    assert result[4] == "mg"


def test_get_missing_item(test_user, test_product):
    with pytest.raises(ValueError, match="Item not found in inventory."):
        test_user.inventory.get_item(test_product)




