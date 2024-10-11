# backend/follows/tasks.py

from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from kafka_app.consumer import KafkaConsumerClient
from django.conf import settings
from .models import Follow
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_follow_event_to_kafka(follow_id, event_type):
    """
    Celery task to send follow events to Kafka.
    """
    producer = KafkaProducerClient()

    try:
        if event_type == 'deleted':
            message = {
                "follow_id": follow_id,
                "action": "deleted"
            }
        else:
            follow = Follow.objects.get(id=follow_id)
            message = {
                "follow_id": follow.id,
                "follower_id": follow.follower.id,
                "following_id": follow.followed.id,
                "created_at": str(follow.created_at),
                "event": event_type
            }

        # Get Kafka topic from settings for better flexibility
        kafka_topic = settings.KAFKA_TOPICS.get('FOLLOW_EVENTS', 'default-follow-topic')
        producer.send_message(kafka_topic, message)

        logger.info(f"Sent Kafka message for follow {event_type}: {message}")
    except Follow.DoesNotExist:
        logger.error(f"Follow with ID {follow_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")


@shared_task
def consume_follow_events():
    """
    Celery task to consume follow events from Kafka.
    """
    kafka_topic = settings.KAFKA_TOPICS.get('FOLLOW_EVENTS', 'default-follow-topic')
    consumer = KafkaConsumerClient(kafka_topic)

    for message in consumer.consume_messages():
        try:
            # Add follow-specific processing logic here if needed
            logger.info(f"Processed follow event: {message}")
        except Exception as e:
            logger.error(f"Error processing follow event: {e}")
