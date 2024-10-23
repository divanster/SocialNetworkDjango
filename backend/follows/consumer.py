import logging
from kafka_app.base_consumer import BaseKafkaConsumer
from django.conf import settings

logger = logging.getLogger(__name__)


class FollowKafkaConsumer(BaseKafkaConsumer):
    def __init__(self):
        # Initialize the BaseKafkaConsumer with the specific topic and group id
        topic = settings.KAFKA_TOPICS.get('FOLLOW_EVENTS', 'default-follow-topic')
        group_id = settings.KAFKA_CONSUMER_GROUP_ID
        super().__init__(topic, group_id)

    def process_message(self, message):
        # Add your custom processing logic for follow events here
        logger.info(f"Processing follow event: {message}")
        # Implement the business logic you need here, such as updating databases or
        # triggering other services


def main():
    # Create an instance of the consumer and start consuming messages
    consumer_client = FollowKafkaConsumer()
    consumer_client.consume_messages()


if __name__ == "__main__":
    main()
