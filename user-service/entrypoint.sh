#!/bin/bash

# Wait for postgres to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z postgres 5432; do
  sleep 1
  echo "Still waiting for PostgreSQL..."
done
echo "PostgreSQL started"

# Create database if it doesn't exist
echo "Checking if database exists..."
PGPASSWORD=postgres psql -h postgres -U postgres -lqt | cut -d \| -f 1 | grep -qw healthcare_user
if [ $? -ne 0 ]; then
  echo "Creating database healthcare_user..."
  PGPASSWORD=postgres psql -h postgres -U postgres -c "CREATE DATABASE healthcare_user;"
  echo "Database created successfully."
else
  echo "Database already exists."
fi

# Apply database migrations
echo "Applying migrations..."
python manage.py makemigrations authentication
python manage.py makemigrations users
python manage.py migrate

# Create superuser if needed
if [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "Creating superuser..."
  python manage.py createsuperuser --noinput --email $DJANGO_SUPERUSER_EMAIL --username admin || true
fi

# Install common-auth if it exists
if [ -d "/common-auth" ]; then
  echo "Installing common-auth..."
  pip install -e /common-auth
  echo "common-auth installed successfully."
fi

# Start server
echo "Starting server..."
exec "$@"
