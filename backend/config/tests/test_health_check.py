# backend/config/tests/test_health_check.py

from django.test import TestCase
from django.urls import reverse
from django.test import override_settings
from unittest.mock import patch


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

    @patch('core.views.connection')
    def test_health_check_database_unhealthy(self, mock_connection):
        """
        Test that health check returns database unhealthy.
        """
        mock_connection.ensure_connection.side_effect = Exception("Database error")
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['database'], 'unhealthy')

    @patch('core.views.redis.Redis.ping')
    def test_health_check_redis_unhealthy(self, mock_redis_ping):
        """
        Test that health check returns redis unhealthy.
        """
        mock_redis_ping.side_effect = Exception("Redis connection error")
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['redis'], 'unhealthy')

    @patch('core.views.KafkaProducer')
    def test_health_check_kafka_unhealthy(self, mock_kafka_producer):
        """
        Test that health check returns kafka unhealthy.
        """
        mock_kafka_producer.side_effect = Exception("Kafka connection error")
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['kafka'], 'unhealthy')
