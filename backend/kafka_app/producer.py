# backend/kafka_app/producer.py

from kafka_app.services import KafkaService

# Keep the old class name so existing tests and imports continue to work:
KafkaProducerClient = KafkaService
