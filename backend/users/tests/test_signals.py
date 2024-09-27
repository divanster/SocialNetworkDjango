# backend/users/tests/test_signals.py

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from unittest.mock import patch, MagicMock
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from users.models import UserProfile
from users.signals import handle_user_post_save
import logging

# Configure logging for the test
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

User = get_user_model()


@override_settings(
    CHANNEL_LAYERS={
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }
)
class UserSignalsTests(TestCase):
    def setUp(self):
        # Get the in-memory channel layer
        self.channel_layer = get_channel_layer()
        # Ensure the channel layer is cleared before each test
        async_to_sync(self.channel_layer.flush)()

    def test_user_profile_created_on_new_user(self):
        user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword'
        )
        # Check that UserProfile is created
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.user, user)
        # Check that message was sent to the channel layer
        received_messages = async_to_sync(self.channel_layer.receive_group)('users')
        event = received_messages[0]
        self.assertEqual(event['type'], 'new_user')
        self.assertEqual(event['user']['username'], 'testuser')

    def test_user_profile_updated_on_existing_user(self):
        # Create user and profile first
        user = User.objects.create_user(
            email='existinguser@example.com',
            username='existinguser',
            password='password123'
        )
        profile = UserProfile.objects.get(user=user)
        # Clear the channel layer
        async_to_sync(self.channel_layer.flush)()
        # Update user
        user.username = 'updateduser'
        user.save()
        # Check that UserProfile exists
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        # Check that message was sent to the channel layer
        received_messages = async_to_sync(self.channel_layer.receive_group)('users')
        event = received_messages[0]
        self.assertEqual(event['type'], 'update_user')
        self.assertEqual(event['user']['username'], 'updateduser')

    def test_user_profile_created_if_missing_on_existing_user(self):
        # Create user without creating profile
        user = User.objects.create_user(
            email='noprofuser@example.com',
            username='noprofuser',
            password='password123'
        )
        UserProfile.objects.filter(
            user=user).delete()  # Delete the profile to simulate missing profile
        # Clear the channel layer
        async_to_sync(self.channel_layer.flush)()
        # Update user
        user.username = 'noprofuser_updated'
        user.save()
        # Check that UserProfile is re-created
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.user, user)
        # Check that message was sent to the channel layer
        received_messages = async_to_sync(self.channel_layer.receive_group)('users')
        event = received_messages[0]
        self.assertEqual(event['type'], 'update_user')
        self.assertEqual(event['user']['username'], 'noprofuser_updated')

    def test_channel_layer_not_available(self):
        # Mock get_channel_layer to return None
        with patch('users.signals.get_channel_layer', return_value=None):
            user = User.objects.create_user(
                email='nochannel@example.com',
                username='nochannel',
                password='password123'
            )
            # Check that UserProfile is created
            self.assertTrue(UserProfile.objects.filter(user=user).exists())
            # Since channel layer is None, no message should be sent
            received_messages = async_to_sync(self.channel_layer.receive_group)('users')
            self.assertEqual(received_messages, [])

    def test_exception_handling_in_signal(self):
        # Simulate an exception when creating UserProfile
        with patch('users.signals.UserProfile.objects.create',
                   side_effect=Exception('Test Exception')):
            with self.assertLogs('users', level='ERROR') as cm:
                User.objects.create_user(
                    email='erroruser@example.com',
                    username='erroruser',
                    password='password123'
                )
                self.assertIn(
                    'Error creating UserProfile for user erroruser: Test Exception',
                    cm.output[0])
            # Ensure UserProfile is not created
            self.assertFalse(
                UserProfile.objects.filter(user__username='erroruser').exists())
