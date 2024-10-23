# backend/posts/tasks.py

from celery import shared_task
from kafka import KafkaProducer, KafkaConsumer
from .models import Post
import logging
from django.conf import settings
import json

logger = logging.getLogger(__name__)


@shared_task
def send_post_event_to_kafka(post_id, event_type):
    """
    Celery task to send post events to Kafka.
    """
    try:
        # Initialize Kafka producer
        producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BROKER_URL,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5
        )

        # Construct message for Kafka based on the event type
        if event_type == 'deleted':
            message = {
                "post_id": post_id,
                "event": "deleted"
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

        kafka_topic = settings.KAFKA_TOPICS.get('POST_EVENTS', 'default-post-topic')
        producer.send(kafka_topic, value=message)
        producer.flush()
        logger.info(f"Sent Kafka message for post {event_type}: {message}")
    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
    finally:
        producer.close()  # Properly close the producer to avoid any open connections


@shared_task
def consume_post_events():
    """
    Celery task to consume post events from Kafka.
    """
    topic = settings.KAFKA_TOPICS.get('POST_EVENTS', 'default-post-topic')
    try:
        # Initialize Kafka consumer
        consumer = KafkaConsumer(
            topic,
            bootstrap_servers=settings.KAFKA_BROKER_URL,
            group_id=settings.KAFKA_CONSUMER_GROUP_ID,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

        for message in consumer:
            try:
                # Convert JSON message to dictionary
                message_value = message.value

                # Extract event details
                event_type = message_value.get('event')
                post_id = message_value.get('post_id')

                # Process post-specific logic based on the event type
                if event_type == 'created':
                    logger.info(
                        f"Processing 'created' post event for post ID: {post_id}")
                elif event_type == 'updated':
                    logger.info(
                        f"Processing 'updated' post event for post ID: {post_id}")
                elif event_type == 'deleted':
                    logger.info(
                        f"Processing 'deleted' post event for post ID: {post_id}")
                else:
                    logger.warning(f"Unknown post event type received: {event_type}")

            except KeyError as e:
                logger.error(f"Missing key in post event message: {e}")
            except Exception as e:
                logger.error(f"Error processing post event: {e}")

    except Exception as e:
        logger.error(f"Error initializing Kafka consumer: {e}")


@shared_task
def process_new_post(post_id):
    """
    Celery task to process a newly created post.
    This function could be used to perform various background actions,
    such as indexing the post for search, sending notifications, etc.
    """
    try:
        # Initialize Kafka producer
        producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BROKER_URL,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5
        )

        post = Post.objects.get(id=post_id)

        # Example processing logic - Sending post to Kafka for analytics or feed
        # distribution
        message = {
            "post_id": post.id,
            "title": post.title,
            "content": post.content,
            "author_id": post.author_id,
            "created_at": str(post.created_at),
            "event": "created"
        }

        kafka_topic = settings.KAFKA_TOPICS.get('POST_EVENTS', 'default-post-topic')
        producer.send(kafka_topic, value=message)
        producer.flush()
        logger.info(f"Processed new post and sent to Kafka: {message}")
    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
    except Exception as e:
        logger.error(f"Error processing new post: {e}")
    finally:
        producer.close()  # Properly close the producer to avoid any open connections
