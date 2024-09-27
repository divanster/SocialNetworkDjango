# backend/kafka_app/tasks.py

from celery import shared_task
from kafka_app.producer import KafkaProducerClient  # Updated import path


@shared_task
def send_to_kafka(topic, message):
    producer = KafkaProducerClient()
    producer.send_message(topic, message)
