from django.test import TestCase
from unittest.mock import patch, MagicMock
from social.models import Post
from tagging.models import TaggedItem
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer

User = get_user_model()


class PostSignalTest(TestCase):

    def setUp(self):
        # Create users for testing
        self.user = User.objects.create_user(
            username='author', email='author@example.com', password='password123'
        )

    @patch('social.signals.send_post_event_to_kafka.delay')
    @patch('social.signals.async_to_sync')
    def test_post_created_signal(self, mock_async_to_sync, mock_kafka_task):
        # Mock the channel layer to avoid real-time WebSocket operations
        mock_channel_layer = MagicMock()
        mock_async_to_sync.return_value = mock_channel_layer

        # Create a post, triggering the post_saved signal
        post = Post.objects.create(
            title='Test Post',
            content='This is a test post content.',
            author_id=self.user.id,
            author_username=self.user.username,
        )

        # Assert Kafka event was triggered
        mock_kafka_task.assert_called_once_with(post.id, 'created')

        # Assert that real-time group message was sent
        mock_channel_layer.group_send.assert_called_once_with(
            'posts',
            {
                'type': 'post_message',
                'event': 'created',
                'post': str(post.id),
                'title': post.title,
                'content': post.content,
            }
        )

    @patch('social.signals.send_post_event_to_kafka.delay')
    @patch('social.signals.async_to_sync')
    def test_post_updated_signal(self, mock_async_to_sync, mock_kafka_task):
        # Mock the channel layer to avoid real-time WebSocket operations
        mock_channel_layer = MagicMock()
        mock_async_to_sync.return_value = mock_channel_layer

        # Create and then update the post, triggering the post_saved signal
        post = Post.objects.create(
            title='Test Post',
            content='This is a test post content.',
            author_id=self.user.id,
            author_username=self.user.username,
        )

        post.title = 'Updated Test Post'
        post.save()

        # Assert Kafka event was triggered for the update
        mock_kafka_task.assert_called_with(post.id, 'updated')

        # Assert that real-time group message was sent for the update
        mock_channel_layer.group_send.assert_called_with(
            'posts',
            {
                'type': 'post_message',
                'event': 'updated',
                'post': str(post.id),
                'title': post.title,
                'content': post.content,
            }
        )

    @patch('social.signals.send_post_event_to_kafka.delay')
    @patch('social.signals.async_to_sync')
    def test_post_deleted_signal(self, mock_async_to_sync, mock_kafka_task):
        # Mock the channel layer to avoid real-time WebSocket operations
        mock_channel_layer = MagicMock()
        mock_async_to_sync.return_value = mock_channel_layer

        # Create a post and then delete it, triggering the post_deleted signal
        post = Post.objects.create(
            title='Test Post',
            content='This is a test post content.',
            author_id=self.user.id,
            author_username=self.user.username,
        )
        post.delete()

        # Assert Kafka event was triggered for deletion
        mock_kafka_task.assert_called_once_with(post.id, 'deleted')

        # Assert that real-time group message was sent for the deletion
        mock_channel_layer.group_send.assert_called_once_with(
            'posts',
            {
                'type': 'post_message',
                'event': 'deleted',
                'post': str(post.id),
                'title': post.title,
                'content': post.content,
            }
        )

    @patch('social.signals.async_to_sync')
    def test_tagged_item_saved_signal(self, mock_async_to_sync):
        # Mock the channel layer to avoid real-time WebSocket operations
        mock_channel_layer = MagicMock()
        mock_async_to_sync.return_value = mock_channel_layer

        # Create a post
        post = Post.objects.create(
            title='Test Post',
            content='This is a test post content.',
            author_id=self.user.id,
            author_username=self.user.username,
        )

        # Create a tagged item, triggering the tagged_item_saved signal
        tagged_item = TaggedItem.objects.create(
            content_object=post,
            tagged_user_id=self.user.id,
            tagged_by=self.user,
        )

        # Assert that real-time group message was sent for tagging
        mock_channel_layer.group_send.assert_called_once_with(
            'posts',
            {
                'type': 'post_message',
                'event': 'tagged',
                'post': str(post.id),
                'title': post.title,
                'content': post.content,
                'tagged_user_ids': [str(tagged_item.tagged_user_id)],
            }
        )

    @patch('social.signals.async_to_sync')
    def test_tagged_item_saved_signal_update(self, mock_async_to_sync):
        # Mock the channel layer to avoid real-time WebSocket operations
        mock_channel_layer = MagicMock()
        mock_async_to_sync.return_value = mock_channel_layer

        # Create a post
        post = Post.objects.create(
            title='Test Post',
            content='This is a test post content.',
            author_id=self.user.id,
            author_username=self.user.username,
        )

        # Create a tagged item
        tagged_item = TaggedItem.objects.create(
            content_object=post,
            tagged_user_id=self.user.id,
            tagged_by=self.user,
        )

        # Update the tagged item, triggering the tagged_item_saved signal for update
        tagged_item.tagged_user_id = self.user.id
        tagged_item.save()

        # Assert that real-time group message was sent for untagging
        mock_channel_layer.group_send.assert_called_with(
            'posts',
            {
                'type': 'post_message',
                'event': 'untagged',
                'post': str(post.id),
                'title': post.title,
                'content': post.content,
                'tagged_user_ids': [str(tagged_item.tagged_user_id)],
            }
        )



