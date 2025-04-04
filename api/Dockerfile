# FROM python:3.9-slim-bullseye

# WORKDIR /app

# # Устанавливаем только необходимый минимум
# RUN apt-get clean && \
#     rm -rf /var/lib/apt/lists/* && \
#     apt-get update -y && \
#     apt-get install -y --no-install-recommends postgresql-client && \
#     apt-get clean && \
#     rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# # Устанавливаем зависимости Python
# COPY requirements.txt .
# RUN pip install --no-cache-dir --upgrade pip && \
#     pip install --no-cache-dir -r requirements.txt

# # Копируем файлы проекта
# COPY . .

# # Создаем директории для статических и медиа файлов
# RUN mkdir -p /staticfiles /media

# # Исправляем проблему с force_text в social_django
# RUN sed -i 's/from django.utils.encoding import force_text/from django.utils.encoding import force_str as force_text/g' /usr/local/lib/python3.9/site-packages/social_django/fields.py

# EXPOSE 8000

# # Запускаем миграции и приложение
# CMD python manage.py migrate && \
#     python manage.py collectstatic --noinput && \
#     gunicorn api.wsgi:application --bind 0.0.0.0:8000

#___________________________________________________________________________________________#

# Используем Python 3.9 в качестве базового образа
FROM python:3.9-slim-bullseye

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости и полезные утилиты для разработки
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    bash \
    git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    librdkafka-dev \
    && pip install confluent-kafka \
    && rm -rf /var/lib/apt/lists/*

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Создаем директории для статики и медиа файлов
RUN mkdir -p /staticfiles /media

# Исправляем проблему с force_text в social_django
RUN sed -i 's/from django.utils.encoding import force_text/from django.utils.encoding import force_str as force_text/g' /usr/local/lib/python3.9/site-packages/social_django/fields.py

# Открываем порт 8000 для приложения
EXPOSE 8000

# Запускаем миграции, собираем статические файлы и запускаем приложение с gunicorn
CMD bash -c "python manage.py migrate && \
             python manage.py collectstatic --noinput && \
             gunicorn api.wsgi:application --bind 0.0.0.0:8000"
