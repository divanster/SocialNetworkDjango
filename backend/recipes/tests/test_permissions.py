from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from recipes.models import Recipe

User = get_user_model()

class RecipePermissionsTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            description='Test Description',
            instructions='Test Instructions',  # Ensure all required fields are provided
            author=self.user
        )
        self.client = APIClient()

    def test_author_can_edit_own_recipe(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('recipe-detail', args=[self.recipe.id])
        data = {'title': 'Updated Recipe'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.recipe.refresh_from_db()
        self.assertEqual(self.recipe.title, 'Updated Recipe')

    def test_non_author_cannot_edit_recipe(self):
        self.client.force_authenticate(user=self.user2)
        url = reverse('recipe-detail', args=[self.recipe.id])
        data = {'title': 'Updated Recipe'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_non_authenticated_user_cannot_edit_recipe(self):
        url = reverse('recipe-detail', args=[self.recipe.id])
        data = {'title': 'Updated Recipe'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
