from backend.database.connections import get_connection
from backend.src.classes.meal import Meal

class Ingredient():
    def __init__(self, 
                 ingredient_id,
                 meal_id,
                 ingredient_type_id,
                 quantity,
                 quantity_unit,
                 connection_choice=get_connection
                 ):
        self.connection_choice = connection_choice
        self.ingredient_id = ingredient_id
        self.meal_id = meal_id
        self.ingredient_type_id = ingredient_type_id
        self.quantity = quantity
        self.quantity_unit = quantity_unit

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
                        raise ValueError("Ingredient doesn't have a type.")
    
                    return result[0]

    def get_meal(self):
                with self.connection_choice() as connection:
                    with connection.cursor() as cursor:
                        cursor.execute(
                            """
                            SELECT user_id, meal, portion, portion_unit
                            FROM meals
                            WHERE meal_id = %s
                            """,
                            (
                                self.meal_id,
                            )
                        )
                        result = cursor.fetchone()
                        if result is None:
                            raise ValueError("Ingredient doesn't match any meals.")
        
                        return Meal(
                             user_id = result[0],
                             meal = result[1],
                             portion = result[2],
                             portion_unit = result[3]
                        )
        
