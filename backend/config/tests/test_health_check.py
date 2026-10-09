# backend/config/tests/test_health_check.py

from django.db.utils import OperationalError
from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch


class HealthCheckTests(TestCase):
    def test_health_check_reports_application_and_database(self):
        """
        Health endpoint should return a deterministic JSON contract for
        application + database status.
        """
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['application'], 'healthy')
        self.assertEqual(response.json()['database'], 'healthy')
        self.assertSetEqual(set(response.json().keys()), {'application', 'database'})

    @patch('core.views.connection.ensure_connection')
    def test_health_check_database_unhealthy(self, mock_ensure_connection):
        """
        DB connectivity failures should return 503 with database=unhealthy.
        """
        mock_ensure_connection.side_effect = OperationalError("Database error")
        response = self.client.get(reverse('health_check'))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()['database'], 'unhealthy')

    def test_health_check_rejects_non_get_methods(self):
        response = self.client.post(reverse('health_check'))
        self.assertEqual(response.status_code, 405)
