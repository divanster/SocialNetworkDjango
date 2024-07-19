FROM python:3.9-alpine3.13

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH="/app:/app/backend"

# Copy requirements files
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Set the working directory
WORKDIR /app
COPY . /app

# Expose port 8000
EXPOSE 8000

# Install dependencies and set up the environment
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev zlib zlib-dev libffi-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    apk add --no-cache graphviz graphviz-dev fontconfig ttf-dejavu && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    /py/bin/pip install gunicorn whitenoise psycopg2-binary pygraphviz && \
    if [ "$DEV" = "true" ]; then /py/bin/pip install -r /tmp/requirements.dev.txt; fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser --disabled-password --no-create-home django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    mkdir -p /app/static && \
    mkdir -p /app/staticfiles && \
    chown -R django-user:django-user /vol/web && \
    chown -R django-user:django-user /app/static && \
    chown -R django-user:django-user /app/staticfiles && \
    chmod -R 777 /vol/web && \
    chmod -R 777 /app/static && \
    chmod -R 777 /app/staticfiles

# Ensure migration_questioner.py is copied after all setup
COPY ./migration_questioner.py /app/migration_questioner.py

# Update PATH environment variable
ENV PATH="/py/bin:$PATH"

# Switch to non-root user
USER django-user

# Command to run the application
CMD ["gunicorn", "--workers=2", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
