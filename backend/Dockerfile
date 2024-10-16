# Use a Debian-based image for better compatibility with confluent-kafka and MongoDB drivers
FROM python:3.10-slim AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/backend" \
    DEV=true

# Set the working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \                          # Install GCC compiler
    g++ \                          # Install G++ compiler
    libc-dev \                     # C standard library for development
    make \                         # Build tool for packages
    libssl-dev \                   # SSL library (e.g., used by MongoDB)
    libsasl2-dev \                 # Required for authentication (MongoDB, Kafka)
    libpq-dev \                    # PostgreSQL development files
    libjpeg-dev \                  # Required for image processing (Pillow)
    zlib1g-dev \                   # Compression library, needed by Pillow
    graphviz \                     # Graph generation tool, useful for visualizations
    libgraphviz-dev \              # Graphviz library for Python bindings
    curl \                         # Utility for transferring data
    bash \                         # Shell to run shell scripts
    libffi-dev \                   # FFI, needed for cryptography packages
    libfreetype6-dev \             # Font rendering, needed by Pillow
    libfontconfig1 \               # Font configuration and customization
    libxrender1 \                  # Rendering library, often needed for graph visualization
    libxml2 \                      # XML library for XML parsing
    libxslt-dev \                  # XSLT processing library
    libxmlsec1-dev \               # XML security library (used by some APIs)
    libxmlsec1-openssl \           # Adds OpenSSL support for XML security
    postgresql-client \            # PostgreSQL client to interact with the database
    netcat-openbsd \               # Utility to help with service readiness checks
    python3-dev \                  # Python development files
    default-libmysqlclient-dev \   # MySQL client, just in case MySQL is used in the project
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Copy requirements files to temporary location
COPY ./requirements.txt ./requirements.dev.txt /tmp/

# Install Python dependencies
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    pip install --no-cache-dir confluent-kafka gunicorn whitenoise psycopg2-binary pygraphviz && \
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

# Copy wait-for-it.sh to /app directory and make it executable
COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh  # Ensure wait-for-it.sh script is executable

# Ensure all files are owned by django-user for security purposes
RUN chown -R django-user:django-user /app

# Expose the port used by Django to handle HTTP requests
EXPOSE 8000

# Switch to non-root user for security purposes
USER django-user

# Define a health check to ensure the application is running correctly
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1

# Command to wait for Kafka to be ready and then start the application using Gunicorn
CMD ["sh", "-c", "./wait-for-it.sh kafka:9093 -- gunicorn --workers=2 --bind 0.0.0.0:8000 config.wsgi:application"]
