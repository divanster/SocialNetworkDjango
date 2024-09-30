from celery import shared_task
from kafka_app.consumer import KafkaConsumerClient
import logging

logger = logging.getLogger(__name__)


@shared_task
def consume_comment_events():
    consumer = KafkaConsumerClient('COMMENT_EVENTS')
    for message in consumer.consume_messages():
        try:
            # Process the comment event message
            event_type = message.get('action', 'created')
            comment_id = message.get('comment_id')

            if event_type == "created":
                # Handle created comments
                logger.info(f"Processed comment creation event: {message}")
            elif event_type == "deleted":
                # Handle deleted comments
                logger.info(f"Processed comment deletion event: {message}")
            else:
                logger.warning(f"Unknown event type: {event_type}")

            # Add any additional processing logic here
        except Exception as e:
            logger.error(f"Error processing comment event: {e}")
