from django.test import TestCase
from django.contrib.auth import get_user_model
from pages.models import Page

User = get_user_model()


class PageModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', email='user1@example.com', password='password123')

    def test_create_page(self):
        page = Page.objects.create(user=self.user, title='Test Page', content='This is test content.')
        self.assertEqual(str(page), 'Test Page')
        self.assertEqual(page.user, self.user)
        self.assertEqual(page.content, 'This is test content.')
