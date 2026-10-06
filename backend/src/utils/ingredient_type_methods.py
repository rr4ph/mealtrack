from backend.database.connections import get_connection

def create_ingredient_type(name, connection_choice=get_connection):
    with connection_choice() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO ingredient_types(name)
                VALUES (%s) 
                """,
                (
                    name,
                )
            )

def merge_ingredient_types(kept_id, deleted_id, connection_choice=get_connection):
    with connection_choice() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE ingredients
                SET ingredient_type_id = %s
                WHERE ingredient_type_id = %s
                """,
                (kept_id, deleted_id)
            )

            cursor.execute(
                """
                UPDATE products
                SET ingredient_type_id = %s
                WHERE ingredient_type_id = %s
                """,
                (kept_id, deleted_id)
            )

            cursor.execute(
                """
                DELETE FROM ingredient_types
                WHERE ingredient_type_id = %s
                """,
                (deleted_id,)
            )

            return True

def get_ingredient_types(connection_choice=get_connection):
    with connection_choice() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT ingredient_type_id, name
                FROM ingredient_types
                ORDER BY name
                """
            )

            return cursor.fetchall()