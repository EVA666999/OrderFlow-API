FROM python:3.9

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install gunicorn==20.1.0

COPY requirements.txt .

RUN pip install -r minimal-requirements.txt --no-cache-dir

COPY . .

# Создаем директорию для логов
RUN mkdir -p /var/log/celery

# Создаем директорию для бэкапов
RUN mkdir -p /app/backups

# Делаем entrypoint исполняемым
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--timeout", "120", "api.wsgi"]