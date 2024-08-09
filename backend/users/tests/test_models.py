from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import UserProfile


class UserModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        user = get_user_model().objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpassword'
        )
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertTrue(user.check_password('testpassword'))

    def test_new_user_email_normalized(self):
        email = 'testuser@EXAMPLE.COM'
        user = get_user_model().objects.create_user(email, 'testpass123')
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'testpass123')

    def test_create_new_superuser(self):
        user = get_user_model().objects.create_superuser(
            'superuser@example.com',
            'superpass123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_user_profile_creation(self):
        user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='testpass123',
            username='testuser'
        )
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.user, user)
