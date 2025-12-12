#!/bin/bash

set -e

echo "Waiting for PostgreSQL..."

while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" > /dev/null 2>&1; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done

echo "PostgreSQL is up - continuing..."

# Install npm dependencies and build Tailwind CSS
echo "Installing npm dependencies..."
npm install --legacy-peer-deps

echo "Building TailwindCSS..."
npx tailwindcss -i ./static/src/input.css -o ./static/css/output.css --minify || echo "TailwindCSS build skipped"

# Create database migrations
echo "Creating database migrations..."
python manage.py makemigrations accounts --noinput
python manage.py makemigrations providers --noinput
python manage.py makemigrations reviews --noinput
python manage.py makemigrations core --noinput

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
echo "Creating superuser if needed..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@findapro.com', 'adminpassword')
    print('Superuser created.')
else:
    print('Superuser already exists.')
EOF

echo "Starting Django development server..."
python manage.py runserver 0.0.0.0:8000
