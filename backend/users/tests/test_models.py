# backend/users/tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model

class UserModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'testuser@example.com'
        username = 'testuser'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            username=username,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""
        email = 'testuser@EXAMPLE.COM'
        username = 'testuser'
        user = get_user_model().objects.create_user(email, username, 'testpass123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'testuser', 'testpass123')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        email = 'superuser@example.com'
        username = 'superuser'
        user = get_user_model().objects.create_superuser(
            email=email,
            username=username,
            password='superpass123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
