FROM python:3.9-slim

WORKDIR /app

# Update and install dependencies with proper key handling
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    wget \
    lsb-release && \
    # Update keyring properly
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update -y && \
    apt-get install -y postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create directories for static and media files
RUN mkdir -p /staticfiles /media

# Fix social_django compatibility issue
RUN sed -i 's/from django.utils.encoding import force_text/from django.utils.encoding import force_str as force_text/g' /usr/local/lib/python3.9/site-packages/social_django/fields.py

EXPOSE 8000

# Run migrations and start the application
CMD python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn api.wsgi:application --bind 0.0.0.0:8000