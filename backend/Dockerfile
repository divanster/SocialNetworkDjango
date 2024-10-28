# Use a Debian-based image for better compatibility with confluent-kafka and MongoDB drivers
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/backend" \
    DEV=true

# Set the working directory
WORKDIR /app

# Install runtime dependencies in smaller groups
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libc-dev make \
    libssl-dev libsasl2-dev libpq-dev \
    libjpeg62-turbo-dev zlib1g-dev && \
    apt-get install -y --no-install-recommends \
    curl bash libffi-dev libfreetype6-dev libfontconfig1 libxrender1 && \
    apt-get install -y --no-install-recommends \
    libxml2 libxslt1-dev libxmlsec1-dev libxmlsec1-openssl \
    postgresql-client netcat-openbsd python3-dev \
    default-libmysqlclient-dev && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Copy requirements files to temporary location
COPY ./requirements.txt ./requirements.dev.txt /tmp/

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir confluent-kafka gunicorn whitenoise psycopg2-binary && \
    if [ "$DEV" = "true" ]; then \
        echo "Installing dev requirements"; \
        pip install --no-cache-dir -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp  # Clean up to reduce image size

# Create a non-root user for running the Django application
RUN useradd -m django-user && \
    mkdir -p /vol/web/media /vol/web/static /app/static /app/staticfiles /app/backend/core && \
    chown -R django-user:django-user /vol/web /app/static /app/staticfiles /app/backend/core

# Copy application code to the Docker image
COPY . /app

# Ensure all files are owned by django-user for security purposes
RUN chown -R django-user:django-user /app

# Expose the port used by Django to handle HTTP requests
EXPOSE 8000

# Switch to non-root user for security purposes
USER django-user

# Define a health check to ensure the application is running correctly
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1

# Command to start the application using Gunicorn
CMD ["sh", "-c", "gunicorn --workers=2 --bind 0.0.0.0:8000 config.wsgi:application"]
