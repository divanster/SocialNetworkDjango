# backend/core/utils.py

from pymongo import MongoClient
from django.conf import settings
from mongoengine import connect, disconnect


def get_mongo_client():
    """
    Utility function to obtain a MongoDB client instance based on the Django settings.
    Connects with or without authentication depending on the presence of MONGO_USER and MONGO_PASSWORD.
    """
    # Disconnect if already connected, to prevent connection conflicts
    disconnect(alias='social_db')

    # Check if all necessary MongoDB settings exist
    if hasattr(settings, 'MONGO_USER') and settings.MONGO_USER:
        client = MongoClient(
            host=settings.MONGO_HOST,
            port=settings.MONGO_PORT,
            username=settings.MONGO_USER if settings.MONGO_USER else None,
            password=settings.MONGO_PASSWORD if settings.MONGO_PASSWORD else None,
            authSource=settings.MONGO_AUTH_SOURCE if settings.MONGO_AUTH_SOURCE else 'admin'
        )
    else:
        # No authentication required
        client = MongoClient(
            host=settings.MONGO_HOST,
            port=settings.MONGO_PORT
        )

    # Ensure that the connection is registered with MongoEngine
    connect(
        db=settings.MONGO_DB_NAME,
        alias='social_db',  # This must match the alias in all your models
        host=settings.MONGO_HOST,
        port=settings.MONGO_PORT
    )

    return client


# Kafka producer utility (already provided by you)
from kafka_app.producer import KafkaProducerClient


def get_kafka_producer():
    """
    Returns a shared instance of KafkaProducerClient for all apps.
    """
    return KafkaProducerClient()
