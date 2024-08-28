FROM python:3.9-alpine3.13

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="/app:/app/backend"
ENV DEV=true

# Set the working directory
WORKDIR /app

# Copy requirements files
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Install dependencies and set up the environment
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache \
        postgresql-client \
        jpeg-dev \
        zlib-dev \
        libffi-dev \
        build-base \
        postgresql-dev \
        musl-dev \
        graphviz \
        graphviz-dev \
        fontconfig \
        ttf-dejavu && \
#        bash && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    /py/bin/pip install gunicorn whitenoise psycopg2-binary pygraphviz && \
    echo "DEV is $DEV" && \
    if [ "$DEV" = "true" ]; then echo "Installing dev requirements"; /py/bin/pip install -r /tmp/requirements.dev.txt; fi && \
    /py/bin/pip list && \
    rm -rf /tmp && \
    adduser --disabled-password --no-create-home django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    mkdir -p /app/static && \
    mkdir -p /app/staticfiles && \
    chown -R django-user:django-user /vol/web && \
    chown -R django-user:django-user /app/static && \
    chown -R django-user:django-user /app/staticfiles

# Ensure migration_questioner.py is copied after all setup
COPY ./migration_questioner.py /app/migration_questioner.py

# Update PATH environment variable
ENV PATH="/py/bin:$PATH"

# Switch to non-root user
USER django-user

# Expose port 8000
EXPOSE 8000

# Command to run the application
CMD ["gunicorn", "--workers=2", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
