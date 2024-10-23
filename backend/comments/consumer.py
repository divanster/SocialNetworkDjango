# backend/comments/consumer.py
import logging
from kafka_app.base_consumer import BaseKafkaConsumer

logger = logging.getLogger(__name__)

class CommentsKafkaConsumer(BaseKafkaConsumer):
    def __init__(self):
        # Initialize with topic and group_id
        super().__init__(topic='comment-events', group_id='comments_group')

    def process_message(self, message):
        try:
            # Process the comment event here
            event_type = message.get('event')
            if event_type == 'created':
                comment_id = message.get('comment_id')
                logger.info(f"[KAFKA] Received 'created' event for comment ID: {comment_id}")
                # Add your comment processing logic here
            elif event_type == 'updated':
                comment_id = message.get('comment_id')
                logger.info(f"[KAFKA] Received 'updated' event for comment ID: {comment_id}")
                # Add your comment processing logic here
            elif event_type == 'deleted':
                comment_id = message.get('comment_id')
                logger.info(f"[KAFKA] Received 'deleted' event for comment ID: {comment_id}")
                # Add your comment processing logic here
            else:
                logger.warning(f"[KAFKA] Unrecognized event type: {event_type}")
        except Exception as e:
            logger.error(f"[KAFKA] Error processing message: {e}")

def main():
    consumer_client = CommentsKafkaConsumer()
    consumer_client.consume_messages()

if __name__ == "__main__":
    main()
