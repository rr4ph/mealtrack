from backend.database.connections import get_connection

class Meal():
    def __init__(self, user_id, name, portion, portion_unit, connection_choice=get_connection):
        self.connection_choice = connection_choice
        self.user_id = user_id
        self.name = name
        self.portion = portion
        self.portion_unit = portion_unit
