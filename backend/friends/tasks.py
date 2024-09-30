from celery import shared_task
from kafka_app.consumer import KafkaConsumerClient
import logging

logger = logging.getLogger(__name__)


@shared_task
def consume_friend_events():
    consumer = KafkaConsumerClient('FRIEND_EVENTS')
    for message in consumer.consume_messages():
        try:
            event_type = message.get('event')
            if event_type == 'created':
                # Process creation logic
                logger.info(
                    f"Processed friend creation event for Friend ID: {message.get('friend_id')}")
            elif event_type == 'deleted':
                # Process deletion logic
                logger.info(
                    f"Processed friend deletion event for Friend ID: {message.get('friend_id')}")
            else:
                logger.info(f"Received unknown friend event: {message}")
        except Exception as e:
            logger.error(f"Error processing friend event: {e}")
