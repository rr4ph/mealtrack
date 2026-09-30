import datetime

class Product():
    def __init__(self, 
                 name, 
                 price, 
                 currency, 
                 supermarket,
                 external_id=None, 
                 brand=None, 
                 pack_size=None, 
                 unit_price=None,
                 unit_currency=None,
                 unit_name=None,
                 in_catalog=True,
                 promotions=None,
                 category=None
                 ):
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
        self.last_price_update_at = datetime.datetime.now()