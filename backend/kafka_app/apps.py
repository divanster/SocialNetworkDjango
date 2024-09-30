# kafka_app/apps.py

from django.apps import AppConfig


class KafkaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'kafka_app'
    verbose_name = 'Kafka Integration'
