# follows/tasks.py
from celery import shared_task
from kafka_app.consumer import KafkaConsumerClient
import logging

logger = logging.getLogger(__name__)

@shared_task
def consume_follow_events():
    consumer = KafkaConsumerClient('FOLLOW_EVENTS')
    for message in consumer.consume_messages():
        try:
            # Process the follow event
            event_type = message.get('event')
            follow_id = message.get('follow')
            logger.info(f"Processed follow event {event_type} for Follow ID: {follow_id}")
            # Add any additional processing logic here
        except Exception as e:
            logger.error(f"Error processing follow event: {e}")
