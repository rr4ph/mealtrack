from backend.database.connections import get_connection
from backend.src.classes.product import Product
from backend.src.utils.enums import SupermarketType

class InventoryItem():
    def __init__(self, inventory_item_id, product_id, inventory_id, quantity, quantity_unit, connection_choice=get_connection):
        self.connection_choice = connection_choice
        self.inventory_item_id = inventory_item_id
        self.product_id = product_id
        self.inventory_id = inventory_id
        self.quantity = quantity
        self.quantity_unit = quantity_unit

    def get_product(self):
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""
                            SELECT  product_id,
                                    external_id,
                                    ingredient_type_id,
                                    name,
                                    price,
                                    currency,
                                    brand,
                                    pack_size,
                                    unit_price,
                                    unit_currency,
                                    unit_name,
                                    supermarket,
                                    last_price_update_at
                            FROM products 
                            WHERE product_id = %s
                            """,
                            (
                                self.product_id,
                            ))
                result = cursor.fetchone()

                if result is None:
                    raise ValueError("This product doesn't exist.")

                return Product(
                    product_id=result[0],
                    external_id=result[1],
                    ingredient_type_id=result[2],
                    name=result[3],
                    price=result[4],
                    currency=result[5],
                    brand=result[6],
                    pack_size=result[7],
                    unit_price=result[8],
                    unit_currency=result[9],
                    unit_name=result[10],
                    supermarket=SupermarketType(result[11]),
                    last_price_update_at=result[12]
                )