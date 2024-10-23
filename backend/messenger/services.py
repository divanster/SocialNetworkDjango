import logging
from .models import Message

logger = logging.getLogger(__name__)


def process_messenger_event(message):
    """
    Process each message received from Kafka.
    Add logic to handle different message events here, such as updating UI,
    notifying users, or saving messages.
    """
    event_type = message.get("event")
    try:
        if event_type == "created":
            # Logic for processing the "created" event.
            logger.info(f"New message created event: {message}")
            # Custom handling can be added here, like notifying users, updating inbox, etc.

        elif event_type == "updated":
            # Logic for processing the "updated" event.
            logger.info(f"Message updated event: {message}")
            # Update any internal state or cache if needed.

        elif event_type == "deleted":
            # Logic for processing the "deleted" event.
            message_id = message.get("message_id")
            if message_id:
                # Attempt to delete the message and log appropriately.
                deleted_count, _ = Message.objects.filter(id=message_id).delete()
                if deleted_count == 0:
                    logger.warning(f"Message with ID {message_id} not found.")
                else:
                    logger.info(f"Message with ID {message_id} deleted successfully.")

        else:
            logger.warning(f"Unknown event type: {event_type}")

    except Exception as e:
        logger.error(f"Error processing message event {message}: {e}")


def create_message(sender, receiver, content):
    """
    Create a new message between sender and receiver.
    """
    try:
        message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=content
        )
        logger.info(
            f"Created new message from {sender} to {receiver}. Message ID: {message.id}")
        return message
    except Exception as e:
        logger.error(f"Error creating message from {sender} to {receiver}: {e}")
        raise e


def update_message(message_id, content):
    """
    Update the content of a specific message.
    """
    try:
        message = Message.objects.get(id=message_id)
        message.content = content
        message.save()
        logger.info(f"Updated message with ID {message.id}")
        return message
    except Message.DoesNotExist:
        logger.error(f"Message with ID {message_id} does not exist.")
        raise
    except Exception as e:
        logger.error(f"Error updating message with ID {message_id}: {e}")
        raise


def delete_message(message_id):
    """
    Delete a specific message by its ID.
    """
    try:
        deleted_count, _ = Message.objects.filter(id=message_id).delete()
        if deleted_count == 0:
            logger.warning(f"Message with ID {message_id} not found.")
        else:
            logger.info(f"Deleted message with ID {message_id} successfully.")
    except Exception as e:
        logger.error(f"Error deleting message with ID {message_id}: {e}")
        raise
