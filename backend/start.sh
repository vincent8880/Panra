#!/bin/bash
set -e  # Exit on error

echo "🚀 Starting Panra backend..."

# Change to backend directory
cd backend

# Run migrations (continue even if some fail - they might already be applied)
echo "📦 Running database migrations..."
python manage.py migrate --noinput || echo "⚠️  Migration warning (some may already be applied)"

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear || echo "⚠️  Static files collection warning"

# Start gunicorn
echo "🌐 Starting Gunicorn server..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 --access-logfile - --error-logfile -









