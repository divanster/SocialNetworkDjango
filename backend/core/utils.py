# backend/core/utils.py

# Kafka producer utility
from kafka_app.producer import KafkaProducerClient


def get_kafka_producer():
    """
    Returns a shared instance of KafkaProducerClient for all apps.
    """
    return KafkaProducerClient()
