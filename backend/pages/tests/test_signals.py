from django.test import TestCase
from unittest.mock import patch
from django.contrib.auth import get_user_model
from pages.models import Page

User = get_user_model()


class PageSignalsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', email='user1@example.com', password='password123')

    @patch('pages.signals.producer.send_message')
    def test_page_created_signal(self, mock_send_message):
        page = Page.objects.create(user=self.user, title='Test Page', content='Some content')
        mock_send_message.assert_called_once_with('PAGE_EVENTS', {
            "page_id": page.id,
            "title": page.title,
            "content": page.content,
            "created_at": str(page.created_at),
            "event": "created"
        })

    @patch('pages.signals.producer.send_message')
    def test_page_deleted_signal(self, mock_send_message):
        page = Page.objects.create(user=self.user, title='Test Page', content='Some content')
        page_id = page.id
        page.delete()
        mock_send_message.assert_called_once_with('PAGE_EVENTS', {
            "page_id": page_id,
            "event": "deleted"
        })
