FROM python:3.9-slim-bullseye

WORKDIR /app

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    postgresql-client \
    bash \  
    git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /staticfiles /media

RUN sed -i 's/from django.utils.encoding import force_text/from django.utils.encoding import force_str as force_text/g' /usr/local/lib/python3.9/site-packages/social_django/fields.py

EXPOSE 8000

CMD bash -c "python manage.py migrate && \
             python manage.py collectstatic --noinput && \
             gunicorn api.wsgi:application --bind 0.0.0.0:8000"