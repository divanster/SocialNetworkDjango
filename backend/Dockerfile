# Use a Debian-based image for better compatibility
FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app"

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libc-dev make \
    libssl-dev libsasl2-dev libpq-dev \
    libjpeg62-turbo-dev zlib1g-dev \
    curl bash libffi-dev libfreetype6-dev libfontconfig1 libxrender1 \
    libxml2 libxslt1-dev libxmlsec1-dev libxmlsec1-openssl \
    postgresql-client netcat-openbsd python3-dev \
    default-libmysqlclient-dev && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Stage 1: Builder
FROM base AS builder
COPY ./requirements.txt ./requirements.dev.txt /app/
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements.dev.txt

# Stage 2: Production
FROM base AS production

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . /app

# Create a non-root user and adjust permissions
RUN useradd -m django-user && \
    chown -R django-user /app

# Switch to non-root user
USER django-user

# Expose the port
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1

# Entry point
CMD ["sh", "-c", "gunicorn --workers=2 --bind 0.0.0.0:8000 config.wsgi:application"]
