import logging
from kafka_app.base_consumer import BaseKafkaConsumer
from django.conf import settings

logger = logging.getLogger(__name__)


class NewsfeedKafkaConsumer(BaseKafkaConsumer):
    def __init__(self):
        topic = settings.KAFKA_TOPICS.get('NEWSFEED_EVENTS', 'default-newsfeed-topic')
        group_id = settings.KAFKA_CONSUMER_GROUP_ID
        super().__init__(topic, group_id)

    def process_message(self, message):
        logger.info(f"Processing newsfeed event: {message}")
        # Add custom business logic here for processing the newsfeed events


def main():
    consumer_client = NewsfeedKafkaConsumer()
    consumer_client.consume_messages()


if __name__ == "__main__":
    main()
