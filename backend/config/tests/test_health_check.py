# backend/config/tests/test_health_check.py

from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch
from redis import ConnectionError as RedisConnectionError
from kafka.errors import NoBrokersAvailable


class HealthCheckTests(TestCase):
    def test_health_check_all_services_healthy(self):
        """
        Test that health check endpoint returns healthy when all services are up.
        """
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['application'], 'healthy')
        self.assertEqual(response.json()['database'], 'healthy')
        self.assertEqual(response.json()['redis'], 'healthy')
        self.assertEqual(response.json()['kafka'], 'healthy')

    @patch('core.views.connection.ensure_connection')
    def test_health_check_database_unhealthy(self, mock_ensure_connection):
        """
        Test that health check returns database unhealthy.
        """
        mock_ensure_connection.side_effect = Exception("Database error")
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['database'], 'unhealthy')

    @patch('redis.Redis.ping')
    def test_health_check_redis_unhealthy(self, mock_redis_ping):
        """
        Test that health check returns redis unhealthy.
        """
        mock_redis_ping.side_effect = RedisConnectionError("Redis connection error")
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['redis'], 'unhealthy')

    @patch('core.views.KafkaProducer')
    def test_health_check_kafka_unhealthy(self, mock_kafka_producer):
        """
        Test that health check returns kafka unhealthy.
        """
        mock_kafka_producer.side_effect = NoBrokersAvailable("Kafka connection error")
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['kafka'], 'unhealthy')
