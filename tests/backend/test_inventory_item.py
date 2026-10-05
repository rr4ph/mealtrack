import pytest

from backend.src.classes.inventory_item import InventoryItem
from backend.src.classes.product import Product
from backend.src.utils.enums import SupermarketType


def test_get_product(db_connection, test_product):
    item = InventoryItem(
        inventory_item_id=1,
        product_id=test_product.product_id,
        inventory_id=1,
        quantity=2,
        quantity_unit="kg",
        connection_choice=db_connection,
    )

    product = item.get_product()

    assert isinstance(product, Product)
    assert product.product_id == test_product.product_id
    assert product.name == test_product.name
    assert product.supermarket == SupermarketType.TESCO


def test_get_missing_product(db_connection):
    item = InventoryItem(
        inventory_item_id=1,
        product_id=999,
        inventory_id=1,
        quantity=1,
        quantity_unit="unit",
        connection_choice=db_connection,
    )

    with pytest.raises(ValueError, match="This product doesn't exist."):
        item.get_product()
