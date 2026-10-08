import os
import psycopg

def get_connection(dbname = "mealtrack"):
    # Build connection string, using environment variables if provided
    # Otherwise rely on psycopg defaults (uses current user, localhost, no password)
    parts = [f"dbname={dbname}"]
    
    if os.environ.get("DB_HOST"):
        parts.append(f"host={os.environ.get('DB_HOST')}")
    if os.environ.get("DB_USER"):
        parts.append(f"user={os.environ.get('DB_USER')}")
    if os.environ.get("DB_PASSWORD"):
        parts.append(f"password={os.environ.get('DB_PASSWORD')}")
    if os.environ.get("DB_PORT"):
        parts.append(f"port={os.environ.get('DB_PORT')}")
    
    connection_string = " ".join(parts)
    return psycopg.connect(connection_string)
