# kafka_app/tasks.py
from celery import shared_task
from kafka_app.producer import KafkaProducerClient
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=10)  # Retry up to 3 times with a delay of 10 seconds
def send_to_kafka(self, topic_key, message):
    try:
        producer = KafkaProducerClient()
        producer.send_message(topic_key, message)
        producer.close()
        logger.info(f"Message sent to topic '{topic_key}': {message}")
    except Exception as e:
        logger.error(f"Failed to send message to Kafka: {e}")
        self.retry(exc=e)  # Retry the task on failure
