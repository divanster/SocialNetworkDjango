from celery import shared_task
from kafka_app.producer import KafkaProducerClient
from kafka_app.consumer import KafkaConsumerClient
from .models import Reaction
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task
def send_reaction_event_to_kafka(reaction_id, event_type):
    """
    Celery task to send reaction events to Kafka.
    """
    producer = KafkaProducerClient()

    try:
        if event_type == 'deleted':
            message = {
                "reaction_id": reaction_id,
                "action": "deleted"
            }
        else:
            reaction = Reaction.objects.get(id=reaction_id)
            message = {
                "reaction_id": reaction.id,
                "user_id": reaction.user.id,
                "post_id": reaction.content_object.id,
                "emoji": reaction.emoji,
                "created_at": str(reaction.created_at),
                "event": event_type,
            }

        producer.send_message('REACTION_EVENTS', message)
        logger.info(f"Sent Kafka message for reaction {event_type}: {message}")
    except Reaction.DoesNotExist:
        logger.error(f"Reaction with ID {reaction_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending Kafka message: {e}")


@shared_task
def consume_reaction_events():
    topic = settings.KAFKA_TOPICS.get('REACTION_EVENTS', 'default-reaction-topic')
    consumer = KafkaConsumerClient(topic)
    for message in consumer.consume_messages():
        try:
            # Add reaction-specific processing logic here
            logger.info(f"Processed reaction event: {message}")
        except Exception as e:
            logger.error(f"Error processing reaction event: {e}")
