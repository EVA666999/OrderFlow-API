FROM python:3.9-slim

WORKDIR /app

# Обновляем и устанавливаем зависимости, используя более надёжный метод
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update -y --allow-insecure-repositories && \
    apt-get install -y --allow-unauthenticated gnupg2 apt-transport-https ca-certificates && \
    mkdir -p /etc/apt/keyrings && \
    apt-get install -y --allow-unauthenticated wget && \
    sh -c 'wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | gpg --dearmor -o /etc/apt/keyrings/postgresql.gpg' && \
    sh -c 'echo "deb [signed-by=/etc/apt/keyrings/postgresql.gpg] http://apt.postgresql.org/pub/repos/apt/ bookworm-pgdg main" > /etc/apt/sources.list.d/pgdg.list' && \
    apt-get update -y --allow-insecure-repositories && \
    apt-get install -y --allow-unauthenticated postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем зависимости Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем файлы проекта
COPY . .

# Создаем директории для статических и медиа файлов
RUN mkdir -p /staticfiles /media

# Исправляем проблему с force_text в social_django
RUN sed -i 's/from django.utils.encoding import force_text/from django.utils.encoding import force_str as force_text/g' /usr/local/lib/python3.9/site-packages/social_django/fields.py

EXPOSE 8000

# Запускаем миграции и приложение
CMD python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn api.wsgi:application --bind 0.0.0.0:8000