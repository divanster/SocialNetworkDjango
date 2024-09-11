FROM python:3.10-alpine3.13

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/backend" \
    DEV=true

# Set the working directory
WORKDIR /app

# Install dependencies and build tools
RUN apk add --no-cache --virtual .build-deps \
        curl gcc g++ make libc-dev linux-headers build-base bash && \
    apk add --no-cache \
        postgresql-client \
        postgresql-dev \
        jpeg-dev \
        zlib-dev \
        libffi-dev \
        musl-dev \
        graphviz \
        graphviz-dev \
        fontconfig \
        redis \
        ttf-dejavu \
        openssl-dev

# Download and compile librdkafka from the source to ensure the latest version
RUN curl -L "https://github.com/edenhill/librdkafka/archive/refs/tags/v1.9.0.tar.gz" -o librdkafka.tar.gz && \
    tar -xzf librdkafka.tar.gz && \
    cd librdkafka-1.9.0 && \
    ./configure && \
    make && \
    make install && \
    cd .. && \
    rm -rf librdkafka-1.9.0 librdkafka.tar.gz

# Create a virtual environment and install Python dependencies
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip

# Copy requirements files
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Install Python dependencies
RUN /py/bin/pip install --no-cache-dir -r /tmp/requirements.txt && \
    /py/bin/pip install --no-cache-dir confluent-kafka && \
    /py/bin/pip install gunicorn whitenoise psycopg2-binary pygraphviz && \
    if [ "$DEV" = "true" ]; then \
        echo "Installing dev requirements"; \
        /py/bin/pip install -r /tmp/requirements.dev.txt; \
    fi && \
    rm -rf /tmp

# Create non-root user and set permissions
RUN adduser --disabled-password --no-create-home django-user && \
    mkdir -p /vol/web/media /vol/web/static /app/static /app/staticfiles /app/backend/core && \
    chown -R django-user:django-user /vol/web /app/static /app/staticfiles /app/backend/core

# Copy the migration script (if needed)
COPY ./core/management/commands/migration_questioner.py /app/backend/core/management/commands/migration_questioner.py

# Update the PATH environment variable to include the virtual environment
ENV PATH="/py/bin:$PATH"

# Switch to non-root user
USER django-user

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--workers=2", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
