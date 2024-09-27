# Use a Debian-based image for better compatibility with confluent-kafka
FROM python:3.10-slim AS base
# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/backend" \
    DEV=true

# Set the working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libc-dev \
    make \
    libssl-dev \
    libsasl2-dev \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    graphviz \
    libgraphviz-dev \
    curl \
    bash \
    libffi-dev \
    libfreetype6-dev \
    libfontconfig1 \
    libxrender1 \
    libxml2 \
    libxslt-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    postgresql-client \
    redis-server && \
    rm -rf /var/lib/apt/lists/*  # Cleans up to reduce image size

# Upgrade pip
RUN pip install --upgrade pip

# Copy requirements files
COPY ./requirements.txt ./requirements.dev.txt /tmp/

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir confluent-kafka gunicorn whitenoise psycopg2-binary pygraphviz && \
    if [ "$DEV" = "true" ]; then \
        echo "Installing dev requirements"; \
        pip install --no-cache-dir -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp

# Create non-root user and set permissions
RUN useradd -m django-user && \
    mkdir -p /vol/web/media /vol/web/static /app/static /app/staticfiles /app/backend/core && \
    chown -R django-user:django-user /vol/web /app/static /app/staticfiles /app/backend/core

# Copy application code
COPY . /app

# Expose the application port
EXPOSE 8000

# Switch to non-root user
USER django-user

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1

# Command to run the application
CMD ["gunicorn", "--workers=2", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
