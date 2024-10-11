# backend/albums/utils.py
from kafka_app.producer import KafkaProducerClient


def get_kafka_producer():
    return KafkaProducerClient()
