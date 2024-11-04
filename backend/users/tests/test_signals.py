from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import UserProfile
from unittest.mock import patch
import logging

User = get_user_model()

# Configure logging for testing
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class UserSignalsTests(TestCase):
    @patch('users.signals.process_user_event_task.delay')
    def test_user_profile_created_on_new_user(self, mock_process_user_event_task):
        """Test that UserProfile is created and Celery task is triggered on new user
        creation."""
        user = User.objects.create_user(
            email='testuser@example.com',
            username='testuser',
            password='testpassword'
        )

        # Check that UserProfile is created
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

        # Check that Celery task is triggered
        mock_process_user_event_task.assert_called_once_with(user.id, 'new_user')

    @patch('users.signals.process_user_event_task.delay')
    def test_user_profile_updated_on_existing_user(self, mock_process_user_event_task):
        """Test that Celery task is triggered when updating an existing user."""
        user = User.objects.create_user(
            email='existinguser@example.com',
            username='existinguser',
            password='password123'
        )

        # Update user information
        user.username = 'updateduser'
        user.save()

        # Check that UserProfile still exists
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

        # Check that Celery task is triggered for profile update
        mock_process_user_event_task.assert_called_once_with(user.id, 'profile_update')

    @patch('users.signals.process_user_event_task.delay')
    def test_user_profile_created_if_missing_on_existing_user(self,
                                                              mock_process_user_event_task):
        """Test that UserProfile is re-created if it is missing and user is updated."""
        user = User.objects.create_user(
            email='noprofuser@example.com',
            username='noprofuser',
            password='password123'
        )

        # Delete the profile to simulate a missing profile scenario
        UserProfile.objects.filter(user=user).delete()
        self.assertFalse(UserProfile.objects.filter(user=user).exists())

        # Update user, which should trigger profile creation via the signal
        user.username = 'noprofuser_updated'
        user.save()

        # Check that UserProfile is re-created
        self.assertTrue(UserProfile.objects.filter(user=user).exists())

        # Check that Celery task is triggered for profile update
        mock_process_user_event_task.assert_called_once_with(user.id, 'profile_update')

    @patch('users.signals.process_user_event_task.delay')
    def test_user_deletion_triggers_celery_task(self, mock_process_user_event_task):
        """Test that deleting a user triggers the Celery task for user deletion."""
        user = User.objects.create_user(
            email='deleteuser@example.com',
            username='deleteuser',
            password='password123'
        )

        user_id = user.id
        user.delete()

        # Check that Celery task is triggered for user deletion
        mock_process_user_event_task.assert_called_once_with(user_id, 'deleted_user')

    @patch('users.signals.process_user_event_task.delay')
    def test_user_profile_creation_error_handling(self, mock_process_user_event_task):
        """Test error handling during UserProfile creation."""
        with patch('users.signals.UserProfile.objects.create',
                   side_effect=Exception('Test Exception')):
            with self.assertLogs('users', level='INFO') as cm:
                User.objects.create_user(
                    email='erroruser@example.com',
                    username='erroruser',
                    password='password123'
                )

                # Ensure the expected error log is present
                self.assertIn(
                    "ERROR:users:Error creating UserProfile for user "
                    "erroruser@example.com: Test Exception",
                    cm.output
                )

            # Ensure that UserProfile was not created due to the exception
            self.assertFalse(
                UserProfile.objects.filter(user__username='erroruser').exists())

    @patch('users.signals.process_user_event_task.delay')
    def test_signal_triggers_on_user_update(self, mock_process_user_event_task):
        """Test that updating user email or other details triggers Celery task"""
        user = User.objects.create_user(
            email='emailtest@example.com',
            username='emailtest',
            password='password123'
        )

        # Update email
        user.email = 'updatedemail@example.com'
        user.save()

        # Verify that the profile update Celery task is triggered
        mock_process_user_event_task.assert_called_once_with(user.id, 'profile_update')


