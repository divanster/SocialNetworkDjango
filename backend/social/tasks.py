import json

from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from kafka_app.consumer import KafkaConsumerClient
from .models import Post
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task
def send_post_event_to_kafka(post_id, event_type):
    """
    Celery task to send post events to Kafka.
    """
    producer = KafkaProducerClient()

    try:
        if event_type == 'deleted':
            message = {
                "post_id": post_id,
                "action": "deleted"
            }
        else:
            post = Post.objects.select_related('author').get(id=post_id)
            message = {
                "post_id": post.id,
                "title": post.title,
                "content": post.content,
                "author_id": post.author.id,
                "created_at": str(post.created_at),
                "event": event_type,
            }

        producer.send_message(settings.KAFKA_TOPICS['POST_EVENTS'], message)
        logger.info(f"Sent Kafka message for post {event_type}: {message}")
    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")

@shared_task
def consume_post_events():
    topic = settings.KAFKA_TOPICS.get('POST_EVENTS', 'default-post-topic')
    consumer = KafkaConsumerClient(topic)
    for message in consumer.consume_messages():
        try:
            # Convert JSON message to dictionary if necessary
            if isinstance(message, str):
                message = json.loads(message)

            # Process post-specific logic
            event_type = message.get('event')
            post_id = message.get('post_id')

            # Add logic for different event types if needed
            if event_type == 'created':
                logger.info(f"Processing created post event for post ID: {post_id}")
            elif event_type == 'updated':
                logger.info(f"Processing updated post event for post ID: {post_id}")
            elif event_type == 'deleted':
                logger.info(f"Processing deleted post event for post ID: {post_id}")
            else:
                logger.warning(f"Unknown post event type received: {event_type}")

        except KeyError as e:
            logger.error(f"Missing key in post event message: {e}")
        except Exception as e:
            logger.error(f"Error processing post event: {e}")


@shared_task
def process_new_post(post_id):
    """
    Celery task to process a newly created post.
    This function could be used to perform various background actions,
    such as indexing the post for search, sending notifications, etc.
    """
    producer = KafkaProducerClient()

    try:
        post = Post.objects.get(id=post_id)

        # Example processing logic - Sending post to Kafka for analytics or feed distribution
        message = {
            "post_id": post.id,
            "title": post.title,
            "content": post.content,
            "author_id": post.author_id,
            "created_at": str(post.created_at),
            "event": "created"
        }

        producer.send_message(
            settings.KAFKA_TOPICS.get('POST_EVENTS', 'default-post-topic'), message)
        logger.info(f"Processed new post and sent to Kafka: {message}")
    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
    except Exception as e:
        logger.error(f"Error processing new post: {e}")
