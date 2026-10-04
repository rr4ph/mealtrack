from backend.database.connections import get_connection
from backend.src.classes.ingredient import Ingredient

class Meal():
    def __init__(self, meal_id, user_id, name, portion, portion_unit, connection_choice=get_connection):
        self.connection_choice = connection_choice
        self.meal_id = meal_id
        self.user_id = user_id
        self.name = name
        self.portion = portion
        self.portion_unit = portion_unit

    def get_ingredients(self):
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT ingredient_id, ingredient_type_id, quantity, quantity_unit
                    FROM ingredients
                    WHERE meal_id = %s
                    """,
                    (
                        self.meal_id,
                    )
                )
                results = cursor.fetchall()
                ingredients = []

                for result in results:
                        ingredient = Ingredient(
                        ingredient_id=result[0],
                        meal_id=self.meal_id,
                        ingredient_type_id=result[1],
                        quantity=result[2],
                        quantity_unit=result[3]     
                        )
                        ingredients.append(ingredient)

                return ingredients
