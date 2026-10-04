import datetime
from backend.database.connections import get_connection
from backend.src.utils.enums import SupermarketType

class Product():
    def __init__(self, 
                 name, 
                 price, 
                 currency, 
                 supermarket,
                 ingredient_type_id=None,
                 product_id=None,
                 external_id=None, 
                 brand=None, 
                 pack_size=None, 
                 unit_price=None,
                 unit_currency=None,
                 unit_name=None,
                 in_catalog=False,
                 promotions=None,
                 category=None,
                 last_price_update_at=None,
                 connection_choice=get_connection
                 ):
        self.connection_choice = connection_choice
        self.ingredient_type_id = ingredient_type_id
        self.product_id = product_id
        self.external_id = external_id
        self.name = name
        self.price = price
        self.currency = currency
        self.brand = brand
        self.pack_size = pack_size
        self.unit_price = unit_price
        self.unit_currency = unit_currency
        self.unit_name = unit_name
        self.in_catalog = in_catalog
        self.promotions = promotions
        self.category = category
        self.supermarket = supermarket
        self.last_price_update_at = (
            last_price_update_at
            if last_price_update_at is not None
            else datetime.datetime.now()
        )

    def get_ingredient_type(self):
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT name
                    FROM ingredient_types
                    WHERE ingredient_type_id = %s
                    """,
                    (
                        self.ingredient_type_id,
                    )
                )
                result = cursor.fetchone()
                if result is None:
                    raise ValueError("Product doesn't have a type.")

                return result[0]

    def save_product(self):
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                if self.product_id is None:
                    cursor.execute(
                        """
                        INSERT INTO products(
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
                        last_price_update_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        RETURNING product_id
                        """,
                        (
                            self.external_id,
                            self.ingredient_type_id,
                            self.name,
                            self.price,
                            self.currency,
                            self.brand,
                            self.pack_size,
                            self.unit_price,
                            self.unit_currency,
                            self.unit_name,
                            self.supermarket.value,
                            self.last_price_update_at
                        ))
                    self.product_id = cursor.fetchone()[0]

                else:
                    cursor.execute(
                        """
                        UPDATE products 
                        SET external_id=%s,
                            ingredient_type_id=%s,
                            name=%s,
                            price=%s,
                            currency=%s,
                            brand=%s,
                            pack_size=%s,
                            unit_price=%s,
                            unit_currency=%s,
                            unit_name=%s,
                            supermarket=%s,
                            last_price_update_at=%s
                        WHERE product_id=%s
                        """,
                        (
                            self.external_id,
                            self.ingredient_type_id,
                            self.name,
                            self.price,
                            self.currency,
                            self.brand,
                            self.pack_size,
                            self.unit_price,
                            self.unit_currency,
                            self.unit_name,
                            self.supermarket.value,
                            self.last_price_update_at,
                            self.product_id
                        ))
                return True
