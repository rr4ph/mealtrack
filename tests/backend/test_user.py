from backend.src.classes.user import User


def test_user_creation_saves_user_and_inventory(db_connection):
    user = User("alice", "password", connection_choice=db_connection)

    result = user.save_user()

    assert result == "User and inventory created successfully."
    assert user.user_id is not None
    assert user.inventory.user_id == user.user_id
    assert user.inventory.inventory_id is not None


def test_user_update(db_connection):
    user = User("alice", "password", connection_choice=db_connection)
    user.save_user()

    original_hash = user.password_hash
    user.username = "alice_updated"
    user.postcode = "G1 1AA"

    result = user.save_user()

    assert result == "User updated successfully."
    assert user.password_hash == original_hash

    with db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT username, postcode
                FROM users
                WHERE user_id = %s
                """,
                (user.user_id,),
            )
            assert cursor.fetchone() == ("alice_updated", "G1 1AA")
