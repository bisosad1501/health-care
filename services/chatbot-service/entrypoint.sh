#!/bin/bash

# Exit on any error
set -e

# Wait for database to be ready
echo "🔄 Waiting for database to be ready..."
while ! nc -z db 3306; do
    echo "⏳ Database not ready yet, waiting..."
    sleep 2
done
echo "✅ Database is ready!"

# Set environment variables
export PYTHONDONTWRITEBYTECODE=1
export PYTHONUNBUFFERED=1

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput --clear || true

# Create migrations for all apps
echo "🔧 Creating migrations..."
python manage.py makemigrations conversations || true
python manage.py makemigrations ai || true
python manage.py makemigrations knowledge || true
python manage.py makemigrations websockets || true

# Run all migrations
echo "🚀 Running database migrations..."
python manage.py migrate --noinput

# Load initial data if available
echo "📚 Loading initial knowledge base data..."
if [ -f "comprehensive_health_knowledge.json" ]; then
    echo "Found comprehensive health knowledge, setting up knowledge base..."
    python demo_knowledge_base.py || true
fi

# Create fixtures directory if it doesn't exist
mkdir -p fixtures

# Load fixtures if they exist
if [ -f "fixtures/knowledge_base.json" ]; then
    echo "📖 Loading knowledge base fixtures..."
    python manage.py loaddata fixtures/knowledge_base.json || true
fi

if [ -f "knowledge/fixtures/initial_data.json" ]; then
    echo "📖 Loading initial knowledge data..."
    python manage.py loaddata knowledge/fixtures/initial_data.json || true
fi

# Create superuser if environment variables are set
if [ "$DJANGO_SUPERUSER_PASSWORD" ] && [ "$DJANGO_SUPERUSER_EMAIL" ]; then
    echo "👤 Creating superuser..."
    python manage.py shell << EOF
from django.contrib.auth.models import User
try:
    if not User.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists():
        User.objects.create_superuser(
            username='$DJANGO_SUPERUSER_EMAIL',
            email='$DJANGO_SUPERUSER_EMAIL',
            password='$DJANGO_SUPERUSER_PASSWORD'
        )
        print('✅ Superuser created successfully!')
    else:
        print('👤 Superuser already exists')
except Exception as e:
    print(f'❌ Error creating superuser: {e}')
EOF
fi

# Run any additional setup commands if provided
if [ "$SETUP_COMMANDS" ]; then
    echo "🔧 Running additional setup commands..."
    eval "$SETUP_COMMANDS"
fi

# Health check
echo "🩺 Running health check..."
python manage.py check --deploy || python manage.py check

echo "🎉 Setup complete! Starting ChatBot service..."

# Start the server
if [ "$1" = "runserver" ]; then
    echo "🚀 Starting development server..."
    exec python manage.py runserver 0.0.0.0:8000
elif [ "$1" = "daphne" ]; then
    echo "🚀 Starting production server with Daphne..."
    exec daphne -b 0.0.0.0 -p 8000 chatbot_service.asgi:application
else
    echo "🚀 Starting with custom command: $@"
    exec "$@"
fi
