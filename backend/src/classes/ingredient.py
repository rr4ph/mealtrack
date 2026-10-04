from backend.database.connections import get_connection
from backend.src.classes.meal import Meal

class Ingredient():
    def __init__(self, 
                 meal_id,
                 ingredient_type_id,
                 quantity,
                 quantity_unit,
                 connection_choice=get_connection,
                 ingredient_id=None
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
                    SELECT user_id, name, portion, portion_unit
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
                        meal_id=self.meal_id,
                        user_id = result[0],
                        name = result[1],
                        portion = result[2],
                        portion_unit = result[3]
                )

    def save_ingredient(self):
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                if self.ingredient_id is None:
                    cursor.execute(
                        """
                        INSERT INTO ingredients(
                        meal_id,
                        ingredient_type_id,
                        quantity,
                        quantity_unit)
                        VALUES (%s,%s,%s,%s)
                        RETURNING ingredient_id
                        """,
                        (
                            self.meal_id,
                            self.ingredient_type_id,
                            self.quantity,
                            self.quantity_unit
                        ))
                    self.ingredient_id = cursor.fetchone()[0]

                else:
                    cursor.execute(
                        """
                        UPDATE ingredients 
                        SET meal_id=%s,
                            ingredient_type_id=%s,
                            quantity=%s,
                            quantity_unit=%s
                        WHERE ingredient_id=%s
                        """,
                        (
                            self.meal_id,
                            self.ingredient_type_id,
                            self.quantity,
                            self.quantity_unit,
                            self.ingredient_id
                        ))
                return True

    def remove_ingredient(self):
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                """DELETE FROM ingredients 
                WHERE ingredient_id = %s
                AND meal_id = %s
                """,
                (
                    self.ingredient_id,
                    self.meal_id
                ))
                if cursor.rowcount == 0:
                    raise ValueError("Ingredient not found.")
                
                return True

    def increase_quantity(self, quantity):
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE ingredients 
                    SET quantity = quantity + %s
                    WHERE ingredient_id = %s
                    AND meal_id = %s 
                    RETURNING quantity
                    """,
                    (
                        quantity,
                        self.ingredient_id,
                        self.meal_id
                    )
                )
                result = cursor.fetchone()
                if result is None:
                    raise ValueError("Ingredient not found in the meal.")

                self.quantity = result[0]
                return self.quantity

    def decrease_quantity(self, quantity):
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE ingredients 
                    SET quantity = quantity - %s
                    WHERE ingredient_id = %s
                    AND meal_id = %s 
                    RETURNING quantity
                    """,
                    (
                        quantity,
                        self.ingredient_id,
                        self.meal_id
                    )
                )
                result = cursor.fetchone()
                if result is None:
                    raise ValueError("Ingredient not found in the meal.")

                self.quantity = result[0]
                return self.quantity
        
