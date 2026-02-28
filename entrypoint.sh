#!/bin/sh
set -e

# Ensure volume mount points exist and are writable.
mkdir -p /app/staticfiles /app/mediafiles
chown -R app:app /app/staticfiles /app/mediafiles

echo "Applying database migrations..."
su-exec app python manage.py migrate --noinput

echo "Collecting static files..."
su-exec app python manage.py collectstatic --noinput

echo "Starting server..."
exec su-exec app "$@"
