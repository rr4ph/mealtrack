from argon2 import PasswordHasher
from backend.database.connections import get_connection
from backend.src.classes.inventory import Inventory

phasher = PasswordHasher()

class User:
    def __init__(self, username, password, connection_choice = get_connection):
        self.connection_choice = connection_choice
        self.user_id = None
        self.username = username
        self.password_hash = phasher.hash(password)
        self.postcode = None
        self.inventory = Inventory(connection_choice)
        self.meals = []

    def save_user(self):
        with self.connection_choice() as connection:
            with connection.cursor() as cursor:
                if self.user_id is None:
                    cursor.execute(
                        """INSERT INTO users(username, password_hash, postcode) 
                        VALUES (%s,%s,%s)
                        RETURNING user_id
                        """,
                        (
                        self.username, 
                        self.password_hash,
                        self.postcode
                        )
                    )
                    self.user_id = cursor.fetchone()[0]
                    self.inventory.create_inventory(self.user_id, cursor)
                    message = "User and inventory created successfully."
                else:
                    cursor.execute(
                        """
                        UPDATE users 
                        SET username = %s,
                            password_hash = %s,
                            postcode = %s
                        WHERE user_id = %s
                        """,
                        (
                            self.username,
                            self.password_hash,
                            self.postcode,
                            self.user_id
                        ))
                    message = "User updated successfully."
            connection.commit()
            return message
