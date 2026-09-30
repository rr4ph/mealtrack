from backend.database.connections import get_connection

class InventoryItem():
    def __init__(self, inventory_item_id, product_id, inventory_id, quantity, quantity_unit, connection_choice=get_connection):
        self.connection_choice = connection_choice
        self.inventory_item_id = inventory_item_id
        self.product_id = product_id
        self.inventory_id = inventory_id
        self.quantity = quantity
        self.quantity_unit = quantity_unit

    def get_product(self):
        raise NotImplementedError