from celery import shared_task
from kafka_app.producer import KafkaProducerClient
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task
def send_reaction_event_to_kafka(reaction_id, event_type):
    """
    Celery task to send reaction events to Kafka and WebSocket.
    """
    producer = KafkaProducerClient()

    try:
        # Dynamically import the Reaction model
        from reactions.models import Reaction

        if event_type == 'deleted':
            # Create message for deleted events
            message = {
                "reaction_id": reaction_id,
                "action": "deleted"
            }
        else:
            # Fetch the instance to prepare message for created or updated events
            reaction = Reaction.objects.get(id=reaction_id)
            message = {
                "reaction_id": reaction.id,
                "user_id": reaction.user.id,
                "post_id": reaction.content_object.id,
                "emoji": reaction.emoji,
                "created_at": str(reaction.created_at),
                "event": event_type,
            }

        # Send the constructed message to the REACTION_EVENTS Kafka topic
        kafka_topic = settings.KAFKA_TOPICS.get('REACTION_EVENTS', 'default-reaction-topic')
        producer.send_message(kafka_topic, message)
        logger.info(f"Sent Kafka message for reaction {event_type}: {message}")

        # Send WebSocket notification if the reaction is created or updated
        if event_type != 'deleted' and hasattr(reaction.content_object, 'author'):
            send_websocket_notification(reaction, message)

    except Reaction.DoesNotExist:
        logger.error(f"Reaction with ID {reaction_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")
    finally:
        producer.close()  # Ensure producer is properly closed


def send_websocket_notification(reaction, message):
    """
    Sends WebSocket notification to the content author if the reactor is not the author.
    """
    try:
        from websocket.consumers import GeneralKafkaConsumer  # Import to avoid circular dependencies
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()

        author_id = reaction.content_object.author.id

        # Avoid notifying if the author is also the one who reacted
        if author_id != reaction.user.id:
            user_group_name = GeneralKafkaConsumer.generate_group_name(author_id)

            # Notify the content author about the reaction event
            async_to_sync(channel_layer.group_send)(
                user_group_name,
                {
                    'type': 'notification_message',
                    'message': f"Reaction {message['event']}: {message}"
                }
            )
            logger.info(
                f"Real-time WebSocket notification sent for reaction event '{message['event']}' with ID {reaction.id}"
            )

    except Exception as e:
        logger.error(f"Error sending WebSocket notification for reaction event: {e}")
