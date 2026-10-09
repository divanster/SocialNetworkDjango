import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class Wave1RegistrationTests(APITestCase):
    signup_url = "/api/v1/users/signup/"
    token_url = "/api/v1/token/"

    @patch("users.views.send_welcome_email.delay")
    def test_signup_success_and_login(self, _mock_welcome_email):
        self.client.defaults["REMOTE_ADDR"] = "10.0.0.11"
        payload = {
            "email": f"wave1-{uuid.uuid4().hex[:8]}@example.com",
            "username": f"wave1user-{uuid.uuid4().hex[:8]}",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
            "profile": {
                "first_name": "Wave",
                "last_name": "One",
            },
        }
        signup_response = self.client.post(self.signup_url, payload, format="json")
        self.assertEqual(signup_response.status_code, status.HTTP_201_CREATED)

        token_response = self.client.post(
            self.token_url,
            {"email": payload["email"], "password": payload["password"]},
            format="json",
        )
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", token_response.data)
        self.assertIn("refresh", token_response.data)

    def test_signup_duplicate_email_returns_4xx(self):
        self.client.defaults["REMOTE_ADDR"] = "10.0.0.12"
        existing_email = f"dup-{uuid.uuid4().hex[:8]}@example.com"
        User.objects.create_user(
            email=existing_email,
            username=f"existing-{uuid.uuid4().hex[:8]}",
            password="StrongPass123!",
        )

        payload = {
            "email": existing_email,
            "username": f"new-{uuid.uuid4().hex[:8]}",
            "password": "StrongPass123!",
            "password2": "StrongPass123!",
        }
        response = self.client.post(self.signup_url, payload, format="json")
        self.assertGreaterEqual(response.status_code, 400)
        self.assertLess(response.status_code, 500)

    def test_signup_invalid_payload_returns_4xx(self):
        self.client.defaults["REMOTE_ADDR"] = "10.0.0.13"
        payload = {
            "email": f"invalid-{uuid.uuid4().hex[:8]}@example.com",
            "username": f"invalid-{uuid.uuid4().hex[:8]}",
            "password": "StrongPass123!",
            # missing password2
        }
        response = self.client.post(self.signup_url, payload, format="json")
        self.assertGreaterEqual(response.status_code, 400)
        self.assertLess(response.status_code, 500)
