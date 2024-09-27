# backend/kafka_app/producer.py

from kafka import KafkaProducer  # Importing from external 'kafka' package
import json


class KafkaProducerClient:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send_message(self, topic, value):
        self.producer.send(topic, value=value)
        self.producer.flush()
