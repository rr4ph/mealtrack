from backend.database.connections import get_connection

class Meal():
    def __init__(self, user_id, name, portion, portion_unit, connection_choice=get_connection, meal_id=None):
        self.connection_choice = connection_choice
        self.meal_id = meal_id
        self.user_id = user_id
        self.name = name
        self.portion = portion
        self.portion_unit = portion_unit

    def get_ingredients(self):
        from backend.src.classes.ingredient import Ingredient
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

    def get_ingredient(self, ingredient_id):
        from backend.src.classes.ingredient import Ingredient
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT ingredient_type_id, quantity, quantity_unit
                    FROM ingredients
                    WHERE meal_id = %s
                    AND ingredient_id = %s
                    """,
                    (
                        self.meal_id,
                        ingredient_id
                    )
                )
                result = cursor.fetchone()

                if result is None:
                        raise ValueError("No ingredient with this ID.")

                return Ingredient(
                        ingredient_id=ingredient_id,
                        meal_id=self.meal_id,
                        ingredient_type_id=result[0],
                        quantity=result[1],
                        quantity_unit=result[2]     
                        )

    def save_meal(self):
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                if self.meal_id is None:
                    cursor.execute(
                        """
                        INSERT INTO meals(
                        user_id,
                        name,
                        portion,
                        portion_unit)
                        VALUES (%s,%s,%s,%s)
                        RETURNING meal_id
                        """,
                        (
                            self.user_id,
                            self.name,
                            self.portion,
                            self.portion_unit
                        ))
                    self.meal_id = cursor.fetchone()[0]

                else:
                    cursor.execute(
                        """
                        UPDATE meals 
                        SET user_id=%s,
                            name=%s,
                            portion=%s,
                            portion_unit=%s
                        WHERE meal_id=%s
                        """,
                        (
                            self.user_id,
                            self.name,
                            self.portion,
                            self.portion_unit,
                            self.meal_id
                        ))
                return True

    def remove_meal(self):
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                """DELETE FROM meals 
                WHERE meal_id = %s
                AND user_id = %s
                """,
                (
                    self.meal_id,
                    self.user_id
                ))
                if cursor.rowcount == 0:
                    raise ValueError("Meal not found.")
                
                return True       

    def get_meals(self):
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT meal_id, name, portion, portion_unit
                    FROM meals
                    WHERE user_id = %s
                    ORDER BY name
                    """,
                    (
                        self.user_id,
                    )
                )

                results = cursor.fetchall()

                return [
                    Meal(
                        meal_id=result[0],
                        user_id=self.user_id,
                        name=result[1],
                        portion=result[2],
                        portion_unit=result[3],
                        connection_choice=self.connection_choice
                    )
                    for result in results
                ]