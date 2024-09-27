# backend/social/tests/test_signals.py

from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from social.models import Post, Tag
from tagging.models import TaggedItem
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from unittest.mock import patch

User = get_user_model()

@override_settings(
    CHANNEL_LAYERS={
        'default': {
            'BACKEND': 'channels.layers.InMemoryChannelLayer',
        },
    }
)
class PostSignalsTests(TestCase):

    def setUp(self):
        self.channel_layer = get_channel_layer()
        async_to_sync(self.channel_layer.flush)()
        self.user = User.objects.create_user(
            email='signaluser@example.com',
            username='signaluser',
            password='signalpassword'
        )

    def test_post_created_signal(self):
        post = Post.objects.create(
            title='Signal Post',
            content='Content for signal post.',
            author=self.user
        )
        received_messages = async_to_sync(self.channel_layer.receive_group)('posts')
        event = received_messages[0]
        self.assertEqual(event['event'], 'created')
        self.assertEqual(event['post'], str(post.id))

    def test_post_updated_signal(self):
        post = Post.objects.create(
            title='Signal Post',
            content='Content for signal post.',
            author=self.user
        )
        async_to_sync(self.channel_layer.flush)()
        post.title = 'Updated Signal Post'
        post.save()
        received_messages = async_to_sync(self.channel_layer.receive_group)('posts')
        event = received_messages[0]
        self.assertEqual(event['event'], 'updated')
        self.assertEqual(event['post'], str(post.id))

    def test_post_deleted_signal(self):
        post = Post.objects.create(
            title='Signal Post',
            content='Content for signal post.',
            author=self.user
        )
        async_to_sync(self.channel_layer.flush)()
        post_id = post.id
        post.delete()
        received_messages = async_to_sync(self.channel_layer.receive_group)('posts')
        event = received_messages[0]
        self.assertEqual(event['event'], 'deleted')
        self.assertEqual(event['post'], str(post_id))

    def test_tagged_item_saved_signal(self):
        post = Post.objects.create(
            title='Tagged Post',
            content='Post with tag.',
            author=self.user
        )
        async_to_sync(self.channel_layer.flush)()
        tagged_user = User.objects.create_user(
            email='taggeduser@example.com',
            username='taggeduser',
            password='taggedpassword'
        )
        tagged_item = TaggedItem.objects.create(
            content_object=post,
            tagged_user=tagged_user,
            tagged_by=self.user
        )
        received_messages = async_to_sync(self.channel_layer.receive_group)('posts')
        event = received_messages[0]
        self.assertEqual(event['event'], 'tagged')
        self.assertEqual(event['post'], str(post.id))
        self.assertIn(str(tagged_user.id), event['tagged_user_ids'])
