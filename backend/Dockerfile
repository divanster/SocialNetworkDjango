# Use a Python base image with a specific version
FROM python:3.9-alpine3.13

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Copy requirements files
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Set working directory
WORKDIR /app

# Copy the entire backend code into the container
COPY . /app

# Expose port 8000 for Django application
EXPOSE 8000

# Install system dependencies and Python packages
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client jpeg-dev && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev zlib zlib-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    /py/bin/pip install gunicorn whitenoise && \
    if [ "$DEV" = "true" ]; then /py/bin/pip install -r /tmp/requirements.dev.txt; fi && \
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol && \
    /py/bin/python manage.py collectstatic --noinput

# Add /py/bin to the PATH environment variable
ENV PATH="/py/bin:$PATH"

# Set the user for running the application
USER django-user

# Command to run the Django application
CMD ["gunicorn", "--workers=2", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
