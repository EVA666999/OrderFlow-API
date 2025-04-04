FROM python:3.9-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем проект
COPY . .

# Создаем директории для статических и медиа файлов
RUN mkdir -p /staticfiles /media

# Исправляем проблему force_text в social_django
RUN sed -i 's/from django.utils.encoding import force_text/from django.utils.encoding import force_str as force_text/g' /usr/local/lib/python3.9/site-packages/social_django/fields.py

EXPOSE 8000

# Добавляем автоматические миграции и сбор статики
CMD python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn api.wsgi:application --bind 0.0.0.0:8000