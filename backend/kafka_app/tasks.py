# backend/kafka_app/tasks.py

from celery import shared_task
from .consumer import CentralKafkaConsumer


@shared_task(bind=True)
def start_central_kafka_consumer(self):
    consumer = CentralKafkaConsumer()
    consumer.consume_messages()
