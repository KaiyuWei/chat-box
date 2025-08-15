#!/bin/bash

echo "Starting chat-box server..."

echo "Waiting for database to be ready..."
echo "Connecting to: Host=${DB_HOST}, User=${DB_USER}, Database=${DB_NAME}"

# Test connection with error output for debugging
echo "Testing database connection..."
if ! mysqladmin ping -h"${DB_HOST}" -u"${DB_USER}" -p"${DB_PASSWORD}" --skip-ssl 2>&1; then
    echo "Initial connection test failed, will keep trying..."
fi

while ! mysqladmin ping -h"${DB_HOST}" -u"${DB_USER}" -p"${DB_PASSWORD}" --skip-ssl --silent 2>/dev/null; do
    echo "Database is unavailable - sleeping"
    echo "Attempting connection with SSL disabled..."
    sleep 2
done

echo "Database is ready!"

# run database migrations
echo "Running database migrations..."
uv run alembic upgrade head

# check migration execution result
if [ $? -eq 0 ]; then
    echo "Database migrations completed successfully!"
else
    echo "Database migrations failed!"
    exit 1
fi

echo "Starting FastAPI server..."
exec uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
