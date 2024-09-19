# First stage: Build librdkafka
FROM alpine:3.18 AS builder

# Install build dependencies
RUN apk add --no-cache --virtual .build-deps \
    curl \
    gcc \
    g++ \
    make \
    libc-dev \
    linux-headers \
    build-base \
    bash && \
    # Set librdkafka version
    export RDKAFKA_VERSION=1.9.0 && \
    # Build librdkafka
    curl -L "https://github.com/edenhill/librdkafka/archive/refs/tags/v${RDKAFKA_VERSION}.tar.gz" -o librdkafka.tar.gz && \
    tar -xzf librdkafka.tar.gz && \
    cd librdkafka-${RDKAFKA_VERSION} && \
    ./configure && \
    make && \
    make install && \
    cd .. && \
    rm -rf librdkafka-${RDKAFKA_VERSION} librdkafka.tar.gz && \
    # Remove build dependencies
    apk del .build-deps

# Second stage: Build the final image
FROM python:3.10-alpine3.18

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/backend" \
    DEV=true

# Set the working directory
WORKDIR /app

# Install runtime dependencies and build tools needed for compiling Python packages
RUN apk add --no-cache \
    postgresql-client \
    postgresql-dev \
    jpeg-dev \
    zlib-dev \
    libffi-dev \
    graphviz \
    graphviz-dev \
    fontconfig \
    redis \
    ttf-dejavu \
    openssl-dev \
    bash \
    musl-dev \
    gcc

# Copy librdkafka from the builder stage
COPY --from=builder /usr/local/lib/librdkafka* /usr/local/lib/
COPY --from=builder /usr/local/include/librdkafka /usr/local/include/librdkafka

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
RUN adduser --disabled-password --no-create-home django-user && \
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
