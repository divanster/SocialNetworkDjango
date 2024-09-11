# backend/kafka/producer.py
from kafka import KafkaProducer
import json


class KafkaProducerClient:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],  # Adjust to your Kafka server config
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send_message(self, topic, value):
        self.producer.send(topic, value=value)
        self.producer.flush()
