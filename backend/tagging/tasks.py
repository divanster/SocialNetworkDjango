from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def consume_tagging_events():
    # Your code for consuming tagging events goes here
    logger.info("Consuming tagging events...")
    # Example: process the event from Kafka or handle your business logic
