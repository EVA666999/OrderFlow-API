#!/bin/bash

set -e

# Ждем, пока PostgreSQL будет доступен
echo "Waiting for PostgreSQL..."
while ! nc -z db1 5432; do
  sleep 0.1
done
echo "PostgreSQL started"

# Ждем, пока Redis будет доступен
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 0.1
done
echo "Redis started"

# Ждем, пока Kafka будет доступен
if [ "$SERVICE_NAME" = "celery_worker" ] || [ "$SERVICE_NAME" = "celery_beat" ]; then
  echo "Waiting for Kafka..."
  while ! nc -z kafka 9092; do
    sleep 0.1
  done
  echo "Kafka started"
fi

# Выполняем миграции
python manage.py migrate

# Собираем статические файлы
python manage.py collectstatic --noinput

# Создаем темы Kafka, если запускается рабочий процесс Celery
if [ "$SERVICE_NAME" = "celery_worker" ]; then
  echo "Creating Kafka topics..."
  python manage.py kafka_topics --create
fi

# Запускаем нужный сервис в зависимости от переменной среды SERVICE_NAME
if [ "$SERVICE_NAME" = "celery_worker" ]; then
  echo "Starting Celery worker..."
  exec celery -A api worker --loglevel=info
elif [ "$SERVICE_NAME" = "celery_beat" ]; then
  echo "Starting Celery beat..."
  exec celery -A api beat --loglevel=info
else
  # По умолчанию запускаем команду, переданную в CMD
  exec "$@"
fi