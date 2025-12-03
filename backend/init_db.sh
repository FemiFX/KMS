#!/bin/bash
# Initialize database and run migrations

echo "Waiting for database to be ready..."
sleep 5

echo "Creating migrations directory..."
flask db init || echo "Migrations already initialized"

echo "Creating initial migration..."
flask db migrate -m "Initial migration" || echo "Migration already exists"

echo "Running migrations..."
flask db upgrade

echo "Database initialized successfully!"
