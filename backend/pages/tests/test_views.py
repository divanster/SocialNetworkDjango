from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from pages.models import Page

User = get_user_model()


class PageViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='user1', email='user1@example.com', password='password123')
        self.client.force_authenticate(user=self.user)
        self.page_data = {
            "title": "Sample Page",
            "content": "This is a sample page content."
        }

    def test_create_page(self):
        response = self.client.post(reverse('page-list'), self.page_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Page.objects.count(), 1)
        page = Page.objects.get()
        self.assertEqual(page.title, 'Sample Page')

    def test_list_pages(self):
        Page.objects.create(user=self.user, title='Page 1', content='Content 1')
        Page.objects.create(user=self.user, title='Page 2', content='Content 2')
        response = self.client.get(reverse('page-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_page(self):
        page = Page.objects.create(user=self.user, title='Test Page', content='Test Content')
        url = reverse('page-detail', kwargs={'pk': page.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Page')

    def test_update_page(self):
        page = Page.objects.create(user=self.user, title='Old Title', content='Old Content')
        url = reverse('page-detail', kwargs={'pk': page.pk})
        data = {'title': 'Updated Title', 'content': 'Updated Content'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        page.refresh_from_db()
        self.assertEqual(page.title, 'Updated Title')

    def test_delete_page(self):
        page = Page.objects.create(user=self.user, title='Page to Delete', content='Some content')
        url = reverse('page-detail', kwargs={'pk': page.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Page.objects.count(), 0)
