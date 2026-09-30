from backend.database.connections import get_connection
from psycopg.errors import UniqueViolation, CheckViolation
from backend.src.classes.inventory_item import InventoryItem

class Inventory():
    def __init__(self, connection_choice=get_connection):
        self.connection_choice = connection_choice
        self.inventory_id = None
        self.user_id = None

    def create_inventory(self, user_id, cursor):
        cursor.execute(
        """
        INSERT INTO user_inventories(user_id)
        VALUES (%s)
        RETURNING inventory_id
        """,
            (
            user_id,
            )
        )
        self.user_id = user_id
        self.inventory_id = cursor.fetchone()[0]

    def add_item(self, product_id, quantity, quantity_unit):
        try:
            with self.connection_choice() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO inventory_items(inventory_id, product_id, quantity, quantity_unit)
                        VALUES (%s,%s,%s,%s)
                        """,
                        (
                            self.inventory_id,
                            product_id,
                            quantity,
                            quantity_unit
                        )
                    )
        except UniqueViolation:
            raise ValueError("Item already exists.")
        
        return "Product has been added successfully."

    def increase_quantity(self, product_id, quantity):
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE inventory_items 
                    SET quantity = quantity + %s
                    WHERE product_id = %s
                    AND inventory_id = %s 
                    RETURNING quantity, quantity_unit
                    """,
                    (
                        quantity,
                        product_id,
                        self.inventory_id
                    )
                )
                result = cursor.fetchone()
                if result is None:
                    raise ValueError("Item not found in inventory.")
                
                return f"Product is now {round(result[0])} {result[1]}."

    def decrease_quantity(self, product_id, quantity):
        try:
            with self.connection_choice() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        UPDATE inventory_items 
                        SET quantity = quantity - %s
                        WHERE product_id = %s
                        AND inventory_id = %s 
                        RETURNING quantity, quantity_unit
                        """,
                        (
                            quantity,
                            product_id,
                            self.inventory_id
                        )
                    )
                    result = cursor.fetchone()

                    if result is None:
                                raise ValueError("Item not found in inventory.")
                            
                    return f"Product is now {round(result[0])} {result[1]}."
        except CheckViolation:
            raise ValueError(f"You don't have enough of this Product.")

        

    def update_item(self, product_id, quantity, quantity_unit):
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """UPDATE inventory_items 
                    SET quantity = %s, quantity_unit = %s
                    WHERE product_id = %s
                    AND inventory_id = %s
                    RETURNING quantity
                    """,
                    (
                        quantity,
                        quantity_unit,
                        product_id,
                        self.inventory_id
                    )
                )
                result = cursor.fetchone()
                if result is None:
                    raise ValueError("Item not found in inventory.")
                
                return f"Product is now {round(result[0])} {quantity_unit}."
                

    def remove_item(self, product_id):
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                """DELETE FROM inventory_items 
                WHERE product_id = %s
                AND inventory_id = %s
                """,
                (
                    product_id,
                    self.inventory_id
                ))
                if cursor.rowcount == 0:
                    raise ValueError("Item not found in inventory.")
                
                return "Item has been removed."

    def get_item(self, product_id):
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT inventory_item_id, product_id, inventory_id, quantity, quantity_unit
                    FROM inventory_items
                    WHERE product_id = %s
                    AND inventory_id = %s
                    """,
                    (
                        product_id,
                        self.inventory_id
                    )
                )
                result = cursor.fetchone()
                if result is None:
                    raise ValueError("Item not found in inventory.")

                return InventoryItem(
                    inventory_item_id=result[0],
                    product_id=result[1],
                    inventory_id=result[2],
                    quantity=result[3],
                    quantity_unit=result[4],
                    connection_choice=self.connection_choice
                )
    
