import datetime
import pytest

from backend.src.classes.product import Product
from backend.src.utils.enums import SupermarketType
from decimal import Decimal


def test_product_defaults():
    before = datetime.datetime.now()

    product = Product(
        "Milk",
        1.50,
        "GBP",
        SupermarketType.TESCO,
    )

    after = datetime.datetime.now()

    assert product.product_id is None
    assert product.external_id is None
    assert product.in_catalog is False
    assert product.promotions is None
    assert product.category is None
    assert before <= product.last_price_update_at <= after


def test_save_new_product(db_connection, test_ingredient_type):
    product = Product(
        "Milk",
        1.50,
        "GBP",
        SupermarketType.TESCO,
        ingredient_type_id=test_ingredient_type,
        external_id="milk-1",
        brand="Test Brand",
        pack_size="2L",
        unit_price=0.75,
        unit_currency="GBP",
        unit_name="litre",
        connection_choice=db_connection,
    )

    assert product.save_product() is True
    assert product.product_id is not None

    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT name, price, supermarket, external_id
                FROM products
                WHERE product_id = %s
                """,
                (product.product_id,),
            )
            assert cursor.fetchone() == (
                "Milk",
                1.50,
                "Tesco",
                "milk-1",
            )


def test_update_product(db_connection, test_product):
    test_product.name = "Updated Tomato"
    test_product.price = 2.49

    assert test_product.save_product() is True

    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT name, price
                FROM products
                WHERE product_id = %s
                """,
                (test_product.product_id,),
            )
            assert cursor.fetchone() == ("Updated Tomato", Decimal("2.49"))


def test_get_ingredient_type(db_connection, test_product):
    assert test_product.get_ingredient_type() == "Tomato"


def test_get_missing_ingredient_type(db_connection):
    product = Product(
        "Unknown",
        1,
        "GBP",
        SupermarketType.TESCO,
        ingredient_type_id=999,
        connection_choice=db_connection,
    )

    with pytest.raises(ValueError, match="Product doesn't have a type."):
        product.get_ingredient_type()


def test_refresh_requires_external_id():
    product = Product(
        "Milk",
        1,
        "GBP",
        SupermarketType.TESCO,
    )

    with pytest.raises(
        ValueError,
        match="Cannot refresh product without an external ID.",
    ):
        product.refresh_from_api()


def test_refresh_rejects_unsupported_supermarket():
    product = Product(
        "Milk",
        1,
        "GBP",
        "Unknown",
        external_id="milk-1",
    )

    with pytest.raises(ValueError, match="Unsupported supermarket"):
        product.refresh_from_api()


def test_refresh_updates_matching_product(monkeypatch, db_connection, test_product):
    from backend.src.supermarkets import tesco

    refreshed = Product(
        "Fresh Tomato",
        2.49,
        "GBP",
        SupermarketType.TESCO,
        external_id="test-product",
        brand="Fresh Brand",
        pack_size="500g",
        unit_price=4.98,
        unit_currency="GBP",
        unit_name="kg",
        in_catalog=True,
        promotions=["Save 20p"],
        category=["Fresh Food"],
    )

    class FakeTesco:
        def get_product(self, query):
            assert query == "Test Tomato"
            return [refreshed]

    monkeypatch.setattr(tesco, "Tesco", FakeTesco)

    assert test_product.refresh_from_api() is True
    assert test_product.name == "Fresh Tomato"
    assert test_product.price == 2.49
    assert test_product.brand == "Fresh Brand"
    assert test_product.promotions == ["Save 20p"]
    assert test_product.category == ["Fresh Food"]


def test_refresh_raises_when_external_id_not_found(monkeypatch, test_product):
    from backend.src.supermarkets import tesco

    class FakeTesco:
        def get_product(self, query):
            return [
                Product(
                    "Other Tomato",
                    1,
                    "GBP",
                    SupermarketType.TESCO,
                    external_id="different-id",
                )
            ]

    monkeypatch.setattr(tesco, "Tesco", FakeTesco)

    with pytest.raises(
        ValueError,
        match="could not be found at Tesco",
    ):
        test_product.refresh_from_api()
