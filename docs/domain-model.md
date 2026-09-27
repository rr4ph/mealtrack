Classes:

@dataclass
class User:
    id: int
    username: str
    password_hash: str
    postcode: str | None
    inventory: Inventory
    meals: list[Meal]

@dataclass
class Product:
    id: int
    external_id: str | None
    ingredient_type_id: int

    name: str
    price: float
    currency: str

    brand: str | None
    pack_size: str | None

    unit_price: float | None
    unit_currency: str | None
    unit_name: str | None

    in_catalog: bool
    promotions: list[str]
    category: list[str] | None

    supermarket: str
    last_price_update_at: datetime


class Inventory:
    def __init__(self):

        self.items: list[InventoryItem] = []

    add_item(self, item):
        ...

    update_item(self, item):
        ...

    remove_item(self, item):
        ...

    get_item(self, product_id):
        ...


@dataclass
class InventoryItem:
    id: int
    product: Product
    quantity: float
    quantity_unit: str

class Meal:
    def __init__(self, name, portion, portion_unit):
        self.name = name
        self.ingredient_list: list[Ingredient] = []
        self.portion = portion
        self.portion_unit = portion_unit

    def cook_meal(self):
        ...

    def update_meal(self):
        -- change name
        -- change portion
        -- change portion_unit

    add_ingredient(self, ingredient):
        ...

    remove_ingredient(self, ingredient):
        ...

    update_ingredient(self, ingredient):
        ...

    

@dataclass
class Ingredient:
    ingredient_type: IngredientType
    quantity: float
    quantity_unit: str

@dataclass
class IngredientType:
    id: int
    name: str

@dataclass
class Shop:
    name: str
    postcode: str
    distance: float
    distance_unit: str
    supermarket_type: str

Relationships:

User
Product
Inventory
InventoryItem
Meal
Ingredient
IngredientType
Shop

User -> Inventory   (1-to-1)
User -> Meal        (1-to-Many)

Inventory -> InventoryItem  (1-to-Many)
Product -> InventoryItem    (1-to-Many)

Meal -> Ingredient (1-to-Many)

IngredientType -> Ingredient (1-to-Many)
IngredientType -> Product (1-to-Many)
