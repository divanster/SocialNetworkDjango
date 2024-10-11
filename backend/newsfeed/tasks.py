# backend/newsfeed/tasks.py

from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from kafka_app.consumer import KafkaConsumerClient
from social.models import Post
from comments.models import Comment
from reactions.models import Reaction
from albums.models import Album
from stories.models import Story
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

MODEL_MAP = {
    'Post': Post,
    'Comment': Comment,
    'Reaction': Reaction,
    'Album': Album,
    'Story': Story,
}

@shared_task
def send_newsfeed_event_to_kafka(object_id, event_type, model_name):
    """
    Celery task to send various newsfeed model events to Kafka.
    """
    producer = KafkaProducerClient()

    try:
        model = MODEL_MAP.get(model_name)
        if not model:
            raise ValueError(f"Unknown model: {model_name}")

        if event_type == 'deleted':
            # Create a message for deleted events with just the object ID and event type
            message = {
                'id': object_id,
                'event_type': event_type,
                'model_name': model_name,
            }
        else:
            # Fetch the instance from the database for created or updated events
            instance = model.objects.get(id=object_id)
            message = {
                'id': instance.id,
                'event_type': event_type,
                'model_name': model_name,
                'data': {
                    'content': getattr(instance, 'content', None),  # Example: adjust as needed per model
                    'created_at': str(getattr(instance, 'created_at', None)),
                    'author_id': getattr(instance, 'author_id', None),
                }
            }

        # Send the constructed message to the NEWSFEED_EVENTS Kafka topic
        producer.send_message('NEWSFEED_EVENTS', message)
        logger.info(f"Sent Kafka message for {model_name} {event_type}: {message}")

    except model.DoesNotExist:
        logger.error(f"{model_name} with ID {object_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")


@shared_task
def consume_newsfeed_events():
    """
    Celery task to consume newsfeed events from Kafka.
    """
    topic = settings.KAFKA_TOPICS.get('NEWSFEED_EVENTS', 'default-newsfeed-topic')
    consumer = KafkaConsumerClient(topic)
    for message in consumer.consume_messages():
        try:
            # Add newsfeed-specific processing logic here for consumed Kafka messages
            logger.info(f"Processed newsfeed event: {message}")
            # Example: Updating search indexes, sending notifications, or updating a newsfeed cache
        except Exception as e:
            logger.error(f"Error processing newsfeed event: {e}")
