# albums/tasks.py
from celery import shared_task
from kafka_app.consumer import KafkaConsumerClient  # Import Kafka Consumer
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_new_album(album_id):
    # Simulate post-creation processing
    print(f'Processing album with ID: {album_id}')

@shared_task
def consume_album_events():
    consumer = KafkaConsumerClient('ALBUM_EVENTS')  # Adjust if ALBUM_EVENTS is the correct topic

    for message in consumer.consume_messages():
        try:
            event_type = message.get('event')
            album_id = message.get('album')
            title = message.get('title')

            if event_type == 'created':
                logger.info(f"Processing 'created' event for Album ID: {album_id} with title: {title}")
                # Add logic here to handle album creation if needed

            elif event_type == 'deleted':
                logger.info(f"Processing 'deleted' event for Album ID: {album_id}")
                # Add logic here to handle album deletion if needed
        except Exception as e:
            logger.error(f"Error processing message: {e}")
