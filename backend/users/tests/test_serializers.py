from django.test import TestCase
from users.serializers import CustomUserSerializer, UserProfileSerializer
from users.models import UserProfile
from django.contrib.auth import get_user_model


class UserSerializerTests(TestCase):

    def test_user_serializer(self):
        user_data = {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'profile': {
                'first_name': 'Test',
                'last_name': 'User',
                'bio': 'Just a test user.'
            }
        }
        serializer = CustomUserSerializer(data=user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, user_data['email'])
        self.assertEqual(user.username, user_data['username'])

    def test_user_profile_serializer(self):
        user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='testpass123'
        )
        profile = UserProfile.objects.get(user=user)
        serializer = UserProfileSerializer(profile)
        self.assertEqual(serializer.data['first_name'], profile.first_name)
