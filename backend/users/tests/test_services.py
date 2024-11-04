from django.test import TestCase
from unittest.mock import patch, MagicMock
from users.models import CustomUser, UserProfile
from users.services import (
    process_user_event,
    handle_user_registration,
    handle_profile_update,
    handle_user_deletion,
)
from notifications.services import create_notification
import logging

logger = logging.getLogger(__name__)


class UserServiceTests(TestCase):
    def setUp(self):
        # Setting up a user for use in tests
        self.user = CustomUser.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword'
        )

    @patch('users.services.handle_user_registration')
    @patch('users.services.handle_profile_update')
    @patch('users.services.handle_user_deletion')
    def test_process_user_event_user_registered(self, mock_handle_user_deletion,
                                                mock_handle_profile_update,
                                                mock_handle_user_registration):
        """Test processing a 'user_registered' event triggers handle_user_registration"""
        data = {
            'event_type': 'user_registered',
            'user_id': self.user.id
        }
        process_user_event(data)
        mock_handle_user_registration.assert_called_once_with(self.user.id)
        mock_handle_profile_update.assert_not_called()
        mock_handle_user_deletion.assert_not_called()

    @patch('users.services.handle_profile_update')
    def test_process_user_event_profile_updated(self, mock_handle_profile_update):
        """Test processing a 'profile_updated' event triggers handle_profile_update"""
        data = {
            'event_type': 'profile_updated',
            'user_id': self.user.id
        }
        process_user_event(data)
        mock_handle_profile_update.assert_called_once_with(self.user.id)

    @patch('users.services.handle_user_deletion')
    def test_process_user_event_user_deleted(self, mock_handle_user_deletion):
        """Test processing a 'user_deleted' event triggers handle_user_deletion"""
        data = {
            'event_type': 'user_deleted',
            'user_id': self.user.id
        }
        process_user_event(data)
        mock_handle_user_deletion.assert_called_once_with(self.user.id)

    def test_process_user_event_unknown_event_type(self):
        """Test processing an unknown event type results in a warning log"""
        data = {
            'event_type': 'unknown_event',
            'user_id': self.user.id
        }
        with self.assertLogs('users', level='WARNING') as cm:
            process_user_event(data)
            self.assertIn("[USER] Unknown event type: unknown_event", cm.output[0])

    @patch('notifications.services.create_notification')
    def test_handle_user_registration(self, mock_create_notification):
        """Test handling user registration: profile creation and notification"""
        handle_user_registration(self.user.id)

        # Verify profile is created
        self.assertTrue(UserProfile.objects.filter(user=self.user).exists())

        # Verify that welcome notification is created
        mock_create_notification.assert_called_once()
        notification_call = mock_create_notification.call_args[0][0]
        self.assertEqual(notification_call['notification_type'], 'welcome')
        self.assertEqual(notification_call['receiver_id'], self.user.id)

    def test_handle_user_registration_user_does_not_exist(self):
        """Test handling user registration with non-existent user logs error"""
        invalid_user_id = 9999
        with self.assertLogs('users', level='ERROR') as cm:
            handle_user_registration(invalid_user_id)
            self.assertIn(
                f"[USER] Cannot create UserProfile, user with ID {invalid_user_id} does not exist.",
                cm.output[0])

    @patch('notifications.services.create_notification')
    def test_handle_profile_update(self, mock_create_notification):
        """Test handling profile update: notification created"""
        handle_profile_update(self.user.id)

        # Verify notification about profile update is created
        mock_create_notification.assert_called_once()
        notification_call = mock_create_notification.call_args[0][0]
        self.assertEqual(notification_call['notification_type'], 'profile_update')
        self.assertEqual(notification_call['receiver_id'], self.user.id)

    def test_handle_profile_update_user_does_not_exist(self):
        """Test handling profile update with non-existent user logs error"""
        invalid_user_id = 9999
        with self.assertLogs('users', level='ERROR') as cm:
            handle_profile_update(invalid_user_id)
            self.assertIn(f"[USER] User with ID {invalid_user_id} does not exist.",
                          cm.output[0])

    @patch('users.models.UserProfile.delete')
    def test_handle_user_deletion(self, mock_delete_profile):
        """Test handling user deletion: user and profile are deleted"""
        handle_user_deletion(self.user.id)

        # Verify that UserProfile's delete method is called
        mock_delete_profile.assert_called_once()

        # Verify that user is deleted
        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(id=self.user.id)

    def test_handle_user_deletion_user_does_not_exist(self):
        """Test handling user deletion with non-existent user logs error"""
        invalid_user_id = 9999
        with self.assertLogs('users', level='ERROR') as cm:
            handle_user_deletion(invalid_user_id)
            self.assertIn(f"[USER] User with ID {invalid_user_id} does not exist.",
                          cm.output[0])


