from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status

class RateLimitTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_token_refresh_rate_limit(self):
        for _ in range(6):  # Exceed the 5 requests per minute limit
            response = self.client.post('/api/token/refresh/', {'refresh': 'invalid_token'})
        self.assertEqual(response.status_code, 429)

    def test_signup_rate_limit(self):
        for _ in range(4):  # Exceed the 3 requests per hour limit
            response = self.client.post('/api/signup/', {'email': 'test@example.com', 'password': 'testpass123'})
        self.assertEqual(response.status_code, 429)
