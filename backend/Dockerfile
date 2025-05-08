# -----------------------------
# Stage 1: Base Image
# -----------------------------
FROM python:3.11-slim AS base

# Unbuffered logs, our code on PYTHONPATH
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app"

WORKDIR /app

# Install system deps, including the native lz4 library
RUN apt-get update && apt-get install -y --no-install-recommends \
      gcc libc-dev make \
      liblz4-dev lz4 \
      libssl-dev libsasl2-dev libpq-dev \
      libjpeg62-turbo-dev zlib1g-dev \
      libffi-dev python3-dev \
      curl bash \
      postgresql-client netcat-openbsd \
      default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip

# -----------------------------
# Stage 2: Builder
# -----------------------------
FROM base AS builder

# Copy only requirements to leverage Docker cache
COPY requirements.txt requirements.dev.txt /app/

# First install the Python lz4 binding, then the rest
RUN pip install --no-cache-dir lz4 \
 && pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir -r requirements.dev.txt

# -----------------------------
# Stage 3: Production
# -----------------------------
FROM base AS production

# Pull in all our compiled site-packages and scripts
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app code
COPY . /app/

# Make wait-for-it executable, set ownership
RUN chmod +x ./wait-for-it.sh \
 && useradd -m django-user \
 && chown -R django-user /app

USER django-user
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/ || exit 1

CMD ["gunicorn", "--workers=2", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
