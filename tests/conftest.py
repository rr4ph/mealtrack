import pytest

from backend.database.connections import get_connection


@pytest.fixture
def db_connection(clean_test_database):
    return lambda: get_connection("mealtrack_test")


@pytest.fixture
def clean_test_database():
    with get_connection("mealtrack_test") as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                TRUNCATE TABLE
                    ingredients,
                    meals,
                    inventory_items,
                    products,
                    ingredient_types,
                    user_inventories,
                    users
                RESTART IDENTITY CASCADE
                """
            )
    yield
    with get_connection("mealtrack_test") as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                TRUNCATE TABLE
                    ingredients,
                    meals,
                    inventory_items,
                    products,
                    ingredient_types,
                    user_inventories,
                    users
                RESTART IDENTITY CASCADE
                """
            )


@pytest.fixture
def test_user(db_connection):
    from backend.src.classes.user import User

    user = User("test", "testpassword", connection_choice=db_connection)
    user.save_user()
    return user


@pytest.fixture
def test_ingredient_type(db_connection):
    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient_types(name)
                VALUES (%s)
                RETURNING ingredient_type_id
                """,
                ("Tomato",),
            )
            return cursor.fetchone()[0]


@pytest.fixture
def test_product(db_connection, test_ingredient_type):
    from backend.src.classes.product import Product
    from backend.src.utils.enums import SupermarketType

    product = Product(
        name="Test Tomato",
        price=1.99,
        currency="GBP",
        supermarket=SupermarketType.TESCO,
        ingredient_type_id=test_ingredient_type,
        external_id="test-product",
        connection_choice=db_connection,
    )
    product.save_product()
    return product


@pytest.fixture
def test_meal(db_connection, test_user):
    from backend.src.classes.meal import Meal

    meal = Meal(
        user_id=test_user.user_id,
        name="Test Meal",
        portion=2,
        portion_unit="portions",
        connection_choice=db_connection,
    )
    meal.save_meal()
    return meal
