# backend/kafka/tasks.py
from celery import shared_task
from .producer import KafkaProducerClient


@shared_task
def send_to_kafka(topic, message):
    producer = KafkaProducerClient()
    producer.send_message(topic, message)
