# users/tests/test_tasks.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock
from users.tasks import process_user_event_task, send_welcome_email, \
    send_profile_update_notification

User = get_user_model()


class UserTasksTests(TestCase):

    @patch('users.tasks.KafkaProducerClient')
    @patch('users.tasks.send_user_websocket_notification')
    def test_process_user_event_task_new_user(self, mock_send_websocket,
                                              MockKafkaProducer):
        """Test that process_user_event_task sends a message to Kafka and triggers a WebSocket notification for a new user."""
        # Arrange
        user = User.objects.create_user(
            email='newuser@example.com',
            username='newuser',
            password='password123'
        )

        mock_producer_instance = MockKafkaProducer.return_value
        mock_producer_instance.send_message = MagicMock()

        # Act
        process_user_event_task(user.id, 'new_user')

        # Assert
        mock_producer_instance.send_message.assert_called_once()
        mock_send_websocket.assert_called_once_with(user, 'new_user')
        MockKafkaProducer.return_value.close.assert_called_once()

    @patch('users.tasks.KafkaProducerClient')
    @patch('users.tasks.send_user_websocket_notification')
    def test_process_user_event_task_profile_update(self, mock_send_websocket,
                                                    MockKafkaProducer):
        """Test that process_user_event_task sends Kafka message and triggers a WebSocket notification for user update."""
        # Arrange
        user = User.objects.create_user(
            email='updateuser@example.com',
            username='updateuser',
            password='password123'
        )

        mock_producer_instance = MockKafkaProducer.return_value
        mock_producer_instance.send_message = MagicMock()

        # Act
        process_user_event_task(user.id, 'profile_update')

        # Assert
        mock_producer_instance.send_message.assert_called_once()
        mock_send_websocket.assert_called_once_with(user, 'profile_update')
        MockKafkaProducer.return_value.close.assert_called_once()

    @patch('users.tasks.create_notification')
    def test_send_welcome_email_task(self, mock_create_notification):
        """Test that send_welcome_email task calls create_notification for a new user."""
        # Arrange
        user = User.objects.create_user(
            email='welcomeuser@example.com',
            username='welcomeuser',
            password='password123'
        )

        # Act
        send_welcome_email(user.id)

        # Assert
        mock_create_notification.assert_called_once_with({
            'sender_id': user.id,
            'sender_username': 'System',
            'receiver_id': user.id,
            'receiver_username': user.username,
            'notification_type': 'welcome',
            'text': f"Welcome to the platform, {user.username}!",
        })

    @patch('users.tasks.create_notification')
    def test_send_profile_update_notification_task(self, mock_create_notification):
        """Test that send_profile_update_notification task calls create_notification for profile updates."""
        # Arrange
        user = User.objects.create_user(
            email='profileupdateuser@example.com',
            username='profileupdateuser',
            password='password123'
        )

        # Act
        send_profile_update_notification(user.id)

        # Assert
        mock_create_notification.assert_called_once_with({
            'sender_id': user.id,
            'sender_username': user.username,
            'receiver_id': user.id,
            'receiver_username': user.username,
            'notification_type': 'profile_update',
            'text': f"Hello {user.username}, your profile has been updated successfully.",
        })

    @patch('users.tasks.KafkaProducerClient')
    def test_process_user_event_task_user_not_exist(self, MockKafkaProducer):
        """Test process_user_event_task when the user does not exist."""
        # Arrange
        non_existent_user_id = 999

        # Act
        process_user_event_task(non_existent_user_id, 'new_user')

        # Assert
        MockKafkaProducer.return_value.send_message.assert_not_called()
        MockKafkaProducer.return_value.close.assert_called_once()

    @patch('users.tasks.create_notification')
    def test_send_welcome_email_user_not_exist(self, mock_create_notification):
        """Test send_welcome_email task when the user does not exist."""
        # Arrange
        non_existent_user_id = 999

        # Act
        send_welcome_email(non_existent_user_id)

        # Assert
        mock_create_notification.assert_not_called()

    @patch('users.tasks.create_notification')
    def test_send_profile_update_notification_user_not_exist(self,
                                                             mock_create_notification):
        """Test send_profile_update_notification task when the user does not exist."""
        # Arrange
        non_existent_user_id = 999

        # Act
        send_profile_update_notification(non_existent_user_id)

        # Assert
        mock_create_notification.assert_not_called()
