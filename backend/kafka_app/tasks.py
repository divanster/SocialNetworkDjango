# backend/kafka_app/tasks.py

from celery import shared_task
from .consumer import KafkaConsumerApp


@shared_task(bind=True)
def start_central_kafka_consumer(self):
    consumer = KafkaConsumerApp()
    consumer.consume_messages()
