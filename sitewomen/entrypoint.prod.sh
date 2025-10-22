#!/bin/sh

echo "Ожидание PostgreSQL..."

until pg_isready -h "$SQL_HOST" -p "$SQL_PORT" > /dev/null 2>&1; do
  sleep 1
done

echo "PostgreSQL готов, запускаю приложение..."
exec "$@"