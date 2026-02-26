#!/bin/sh
set -e

# Ensure the staticfiles volume mount is writable by the app user.
# Named volumes are created as root; this fixes ownership on first run
# and is a no-op when permissions are already correct.
chown -R app:app /app/staticfiles

echo "Applying database migrations..."
gosu app python manage.py migrate --noinput

echo "Collecting static files..."
gosu app python manage.py collectstatic --noinput

echo "Starting server..."
exec gosu app "$@"
