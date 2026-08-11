#!/bin/sh

set -e

echo "========================================="
echo "Starting SmartHire ATS..."
echo "========================================="

echo "Waiting for PostgreSQL..."

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"
do
    echo "PostgreSQL is unavailable - sleeping..."
    sleep 2
done

echo "PostgreSQL is ready."

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput


echo "Starting Daphne..."

exec daphne \
    -b 0.0.0.0 \
    -p "${PORT:-8000}" \
    config.asgi:application