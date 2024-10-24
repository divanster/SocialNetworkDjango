# backend/core/utils.py

from django.conf import settings
from pymongo import MongoClient


def get_mongo_client():
    """
    Returns a MongoDB client instance using settings from Django.
    """
    return MongoClient(
        host=settings.MONGO_HOST,
        port=settings.MONGO_PORT,
        username=settings.MONGO_USER,
        password=settings.MONGO_PASSWORD,
        authSource=settings.MONGO_AUTH_SOURCE,
    )


# Kafka producer utility (already provided by you)
from kafka_app.producer import KafkaProducerClient


def get_kafka_producer():
    """
    Returns a shared instance of KafkaProducerClient for all apps.
    """
    return KafkaProducerClient()
