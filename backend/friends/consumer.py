import logging
from kafka_app.base_consumer import BaseKafkaConsumer
from django.conf import settings

logger = logging.getLogger(__name__)


class FriendKafkaConsumer(BaseKafkaConsumer):
    def __init__(self):
        # Initialize the BaseKafkaConsumer with the specific topic and group id
        topic = settings.KAFKA_TOPICS.get('FRIEND_EVENTS', 'default-friend-topic')
        group_id = settings.KAFKA_CONSUMER_GROUP_ID
        super().__init__(topic, group_id)

    def process_message(self, message):
        # Add your custom processing logic for friend events here
        logger.info(f"Processing friend event: {message}")
        # Implement the business logic you need here, such as updating databases or
        # triggering other services


def main():
    # Create an instance of the consumer and start consuming messages
    consumer_client = FriendKafkaConsumer()
    consumer_client.consume_messages()


if __name__ == "__main__":
    main()
