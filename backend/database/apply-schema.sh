#!/bin/bash
set -e

# Apply schema to both databases
# In docker-entrypoint-initdb.d, we're running as the postgres user with psql available
SCHEMA_FILE="/schema.sql"

echo "Applying schema to mealtrack database..."
psql -U "$POSTGRES_USER" -d mealtrack -f "$SCHEMA_FILE"

echo "Applying schema to mealtrack_test database..."
psql -U "$POSTGRES_USER" -d mealtrack_test -f "$SCHEMA_FILE"

echo "Database initialization complete"
