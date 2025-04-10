#!/bin/bash

set -e

# Function to check if postgres is ready
postgres_ready() {
    python << END
import sys
import psycopg2
import os
import dj_database_url

try:
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        db_url = 'postgres://postgres:postgres@postgres:5432/healthcare_pharmacy'
    
    config = dj_database_url.parse(db_url)
    conn = psycopg2.connect(
        dbname=config['NAME'],
        user=config['USER'],
        password=config['PASSWORD'],
        host=config['HOST'],
        port=config['PORT']
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

# Wait for postgres to be ready
until postgres_ready; do
    echo "PostgreSQL is unavailable - waiting..."
    sleep 2
done
echo "PostgreSQL is up - continuing..."

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser if needed
if [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser..."
    python manage.py createsuperuser --noinput --email $DJANGO_SUPERUSER_EMAIL || true
fi

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start server
echo "Starting server..."
exec "$@"
