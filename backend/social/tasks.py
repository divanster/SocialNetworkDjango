# backend/social/tasks.py

import logging
from celery import shared_task
from django.conf import settings
from social.models import Post
from core.utils import get_kafka_producer  # or your custom import
from kafka import KafkaConsumer
import json

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=5, default_retry_delay=10)
def send_post_event_to_kafka(self, post_id, event_type):
    """
    Celery task to send post events to Kafka, ensuring all UUID fields become strings.
    """
    try:
        producer = get_kafka_producer()  # must be your KafkaProducerClient if you want encryption + UUIDEncoder

        if event_type == 'deleted':
            # Convert post_id (UUID) to str
            message = {
                "post_id": str(post_id),
                "event": "deleted",
            }
        else:
            post = Post.objects.select_related('user').get(id=post_id)
            # Convert both post.id and user.id (if they are UUID) to str
            message = {
                "post_id": str(post.id),
                "title": post.title,
                "content": post.content,
                "user_id": str(post.user.id),
                "user_username": post.user.username,
                "visibility": post.visibility,
                "created_at": str(post.created_at),
                "event": event_type,
            }

        kafka_topic = settings.KAFKA_TOPICS.get('POST_EVENTS', 'default-post-topic')

        # If your `producer` is your KafkaProducerClient with encryption:
        #  it should call `encrypt_message` -> `UUIDEncoder`.
        #  This ensures no raw UUID remain.
        producer.send(kafka_topic, value=message)
        producer.flush()
        logger.info(f"Sent Kafka message for post {event_type}: {message}")

    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message for post {post_id}: {e}")
        self.retry(exc=e)
    finally:
        # close producer
        producer.close()


@shared_task
def consume_post_events():
    """
    Example Celery task to consume post events from Kafka, if you want to do something else with them.
    """
    topic = settings.KAFKA_TOPICS.get('POST_EVENTS', 'default-post-topic')
    try:
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=settings.KAFKA_BROKER_URL,
            group_id=settings.KAFKA_CONSUMER_GROUP_ID,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        logger.info(f"Consuming messages from {topic} ...")
        for message in consumer:
            try:
                process_kafka_message(message.value)
            except Exception as e:
                logger.error(f"Error processing Kafka message: {e}")
    except Exception as e:
        logger.error(f"Error initializing Kafka consumer: {e}")


@shared_task
def process_kafka_message(message):
    """
    Process a single Kafka message.
    """
    try:
        if not isinstance(message, dict):
            raise ValueError(f"Invalid message format: {message}")

        event_type = message.get('event')
        post_id = message.get('post_id')
        if not event_type or not post_id:
            raise KeyError(f"Missing required keys in Kafka message: {message}")

        # Example: just log the event type
        if event_type == 'created':
            logger.info(f"Kafka event 'created' for post ID {post_id}")
        elif event_type == 'updated':
            logger.info(f"Kafka event 'updated' for post ID {post_id}")
        elif event_type == 'deleted':
            logger.info(f"Kafka event 'deleted' for post ID {post_id}")
        else:
            logger.warning(f"Unknown post event type: {event_type}")

    except (KeyError, ValueError) as e:
        logger.error(f"Kafka message error: {e}")
    except Exception as e:
        logger.error(f"Error processing Kafka message: {e}")
