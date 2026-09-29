import psycopg

def get_connection(dbname = "mealtrack"):
    return psycopg.connect(f"dbname={dbname}")