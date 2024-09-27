# backend/kafka_app/consumer.py

from kafka import KafkaConsumer  # Importing from external 'kafka' package
import json

class KafkaConsumerClient:
    def __init__(self, topic):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id='my-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

    def consume_messages(self):
        for message in self.consumer:
            print(f"Received message: {message.value}")
