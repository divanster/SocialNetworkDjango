# backend/core/utils.py
from kafka_app.producer import KafkaProducerClient


def get_kafka_producer():
    """
    Returns a shared instance of KafkaProducerClient for all apps.
    This utility function can be reused across the entire project.
    """
    return KafkaProducerClient()
