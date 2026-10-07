"""Test to verify ingredient types are persisted through the product search and inventory add flow."""
import pytest
from backend.src.classes.product import Product
from backend.src.utils.enums import SupermarketType
from backend.database.connections import get_connection


@pytest.fixture
def test_ingredient_type():
    """Create a test ingredient type."""
    with get_connection("mealtrack_test") as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO ingredient_types(name) VALUES (%s) RETURNING ingredient_type_id",
                ("Tomato",)
            )
            type_id = cursor.fetchone()[0]
    
    yield type_id
    
    with get_connection("mealtrack_test") as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM ingredient_types WHERE ingredient_type_id = %s", (type_id,))


def test_product_from_supermarket_persists_ingredient_type_when_auto_assigned(test_ingredient_type):
    """When a product is found from supermarket search, auto-assign should find the matching ingredient type."""
    # Create product like Morrisons would return it
    product = Product(
        external_id="TESCO_TOMATO_001",
        name="Tomato Sauce 400g",
        brand="Heinz",
        pack_size="400g",
        price=1.50,
        currency="GBP",
        unit_price=0.375,
        unit_currency="GBP",
        unit_name="100g",
        supermarket=SupermarketType.TESCO,
        category=["Sauces", "Tomato"],
        connection_choice=lambda: get_connection("mealtrack_test"),
    )
    
    # Verify no ingredient type assigned yet
    assert product.ingredient_type_id is None
    
    # Auto-assign should match it
    product.auto_assign_ingredient_type()
    assert product.ingredient_type_id == test_ingredient_type
    
    # Save to database
    product.save_product()
    
    # Verify it was persisted in DB
    with get_connection("mealtrack_test") as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT ingredient_type_id FROM products WHERE external_id = %s",
                ("TESCO_TOMATO_001",)
            )
            row = cursor.fetchone()
            assert row is not None
            assert row[0] == test_ingredient_type
    
    # Clean up
    with get_connection("mealtrack_test") as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM products WHERE external_id = %s",
                ("TESCO_TOMATO_001",)
            )


def test_product_without_match_remains_unclassified():
    """When no matching ingredient type is found, product should remain unclassified."""
    product = Product(
        external_id="UNKNOWN_001",
        name="Random Chocolate Cookies",
        brand="Store Brand",
        pack_size="200g",
        price=1.00,
        currency="GBP",
        supermarket=SupermarketType.TESCO,
        category=["Biscuits"],
        connection_choice=lambda: get_connection("mealtrack_test"),
    )
    
    product.auto_assign_ingredient_type()
    
    # Should have no ingredient type assigned
    assert product.ingredient_type_id is None
    
    # Save it
    product.save_product()
    
    # Verify it's None in DB
    with get_connection("mealtrack_test") as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT ingredient_type_id FROM products WHERE external_id = %s",
                ("UNKNOWN_001",)
            )
            row = cursor.fetchone()
            assert row is not None
            assert row[0] is None
    
    # Clean up
    with get_connection("mealtrack_test") as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM products WHERE external_id = %s",
                ("UNKNOWN_001",)
            )


def test_bread_product_with_category_no_product_name_match(db_connection):
    """Regression test: Bread-like products should match even if 'bread' is not in product name.

    This tests the specific bug where Kingsmill 5050 Thick 800g has category
    ['Bakery & Cakes', 'Bread', ...] but the product name doesn't contain 'bread'.
    The matching should still work through category matching.
    """
    from backend.src.utils.ingredient_matching import best_ingredient_type_id
    from backend.src.utils.ingredient_type_methods import get_ingredient_types, create_ingredient_type

    bread_id = create_ingredient_type("Bread", db_connection)

    product = {
        "name": "Kingsmill 5050 Thick 800g",
        "category": ["Bakery & Cakes", "Bread", "Half & Half Bread"],
    }

    ingredient_types = get_ingredient_types(db_connection)
    result = best_ingredient_type_id(product, ingredient_types)

    assert result == bread_id, f"Expected Bread ({bread_id}), got {result}"
