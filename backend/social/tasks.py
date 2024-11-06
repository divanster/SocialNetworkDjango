from celery import shared_task
from kafka import KafkaProducer, KafkaConsumer
import logging
from django.conf import settings
import json
from social.models import Post
from core.utils import get_kafka_producer

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=5, default_retry_delay=10)
def send_post_event_to_kafka(self, post_id, event_type):
    """
    Celery task to send post events to Kafka and trigger real-time WebSocket notifications.
    """
    producer = get_kafka_producer()

    try:
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
                "author_username": post.author.username,
                "visibility": post.visibility,
                "created_at": str(post.created_at),
                "event": event_type,
            }

        # Get Kafka topic from settings
        kafka_topic = settings.KAFKA_TOPICS.get('POST_EVENTS', 'default-post-topic')
        producer.send(kafka_topic, value=json.dumps(message).encode('utf-8'))
        producer.flush()
        logger.info(f"Sent Kafka message for post {event_type}: {message}")

        # Trigger WebSocket notifications if the event is not a deletion
        if event_type != 'deleted':
            send_websocket_notification(post, event_type)

    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message for post {post_id}: {e}")
        self.retry(exc=e)  # Retry if there's an error
    finally:
        producer.close()  # Properly close the producer to avoid any open connections


def send_websocket_notification(post, event_type):
    """
    Send real-time WebSocket notifications based on the post's visibility.
    """
    try:
        from websocket.consumers import GeneralKafkaConsumer  # Import to avoid circular dependencies
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        from core.utils import get_friends

        channel_layer = get_channel_layer()

        if post.visibility == 'public':
            # Notify all users for public posts
            async_to_sync(channel_layer.group_send)(
                'posts_updates',
                {
                    'type': 'post_message',
                    'event': event_type,
                    'post': str(post.id),
                    'title': post.title,
                    'content': post.content,
                }
            )
        elif post.visibility == 'friends':
            # Notify friends of the author
            friends = get_friends(post.author)
            for friend in friends:
                user_group_name = GeneralKafkaConsumer.generate_group_name(friend.id)
                async_to_sync(channel_layer.group_send)(
                    user_group_name,
                    {
                        'type': 'post_message',
                        'event': event_type,
                        'post': str(post.id),
                        'title': post.title,
                        'content': post.content,
                    }
                )
        elif post.visibility == 'private':
            # Notify only the author for private posts
            user_group_name = GeneralKafkaConsumer.generate_group_name(post.author.id)
            async_to_sync(channel_layer.group_send)(
                user_group_name,
                {
                    'type': 'post_message',
                    'event': event_type,
                    'post': str(post.id),
                    'title': post.title,
                    'content': post.content,
                }
            )
        logger.info(f"Real-time WebSocket notification sent for post event '{event_type}' with ID {post.id}")

    except Exception as e:
        logger.error(f"Error sending WebSocket notification for post {post.id}: {e}")


@shared_task(bind=True, max_retries=5, default_retry_delay=10)
def process_new_post(self, post_id):
    """
    Celery task to process a newly created post.
    This function could be used to perform various background actions,
    such as indexing the post for search, sending notifications, etc.
    """
    producer = get_kafka_producer()

    try:
        post = Post.objects.select_related('author').get(id=post_id)

        # Example processing logic - Sending post to Kafka for analytics or feed distribution
        message = {
            "post_id": post.id,
            "title": post.title,
            "content": post.content,
            "author_id": post.author_id,
            "author_username": post.author.username,
            "visibility": post.visibility,
            "created_at": str(post.created_at),
            "event": "created"
        }

        kafka_topic = settings.KAFKA_TOPICS.get('POST_EVENTS', 'default-post-topic')
        producer.send(kafka_topic, value=json.dumps(message).encode('utf-8'))
        producer.flush()
        logger.info(f"Processed new post and sent to Kafka: {message}")

        # Trigger WebSocket notifications
        send_websocket_notification(post, "created")

    except Post.DoesNotExist:
        logger.error(f"Post with ID {post_id} does not exist.")
    except Exception as e:
        logger.error(f"Error processing new post with ID {post_id}: {e}")
        self.retry(exc=e)  # Retry if there's an error
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
                    logger.info(f"Processing 'created' post event for post ID: {post_id}")
                elif event_type == 'updated':
                    logger.info(f"Processing 'updated' post event for post ID: {post_id}")
                elif event_type == 'deleted':
                    logger.info(f"Processing 'deleted' post event for post ID: {post_id}")
                else:
                    logger.warning(f"Unknown post event type received: {event_type}")

            except KeyError as e:
                logger.error(f"Missing key in post event message: {e}")
            except Exception as e:
                logger.error(f"Error processing post event: {e}")

    except Exception as e:
        logger.error(f"Error initializing Kafka consumer: {e}")
