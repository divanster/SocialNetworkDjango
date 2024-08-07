from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from social.models import Recipe

User = get_user_model()

class RecipeAPITests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        Recipe.objects.all().delete()

    def test_create_recipe(self):
        url = reverse('recipe-list')
        data = {
            'title': 'Test ReactRouterBootstrap',
            'description': 'Test Description',
            'instructions': 'Test Instructions',  # Ensure all required fields are provided
            'tags': [{'name': 'Tag1'}, {'name': 'Tag2'}],
            'ingredients': [{'name': 'Ingredient1'}, {'name': 'Ingredient2'}],
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 1)
        self.assertEqual(Recipe.objects.get().title, 'Test ReactRouterBootstrap')

    def test_get_recipe_list(self):
        Recipe.objects.create(
            title='Test ReactRouterBootstrap 1',
            description='Test Description 1',
            instructions='Test Instructions 1',  # Ensure all required fields are provided
            author=self.user
        )
        Recipe.objects.create(
            title='Test ReactRouterBootstrap 2',
            description='Test Description 2',
            instructions='Test Instructions 2',  # Ensure all required fields are provided
            author=self.user
        )
        url = reverse('recipe-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)

    def test_get_recipe_detail(self):
        recipe = Recipe.objects.create(
            title='Test ReactRouterBootstrap',
            description='Test Description',
            instructions='Test Instructions',  # Ensure all required fields are provided
            author=self.user
        )
        url = reverse('recipe-detail', kwargs={'pk': recipe.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], recipe.title)

    def test_update_recipe(self):
        recipe = Recipe.objects.create(
            title='Test ReactRouterBootstrap',
            description='Test Description',
            instructions='Test Instructions',  # Ensure all required fields are provided
            author=self.user
        )
        url = reverse('recipe-detail', kwargs={'pk': recipe.pk})
        data = {
            'title': 'Updated ReactRouterBootstrap',
            'description': 'Updated Description',
            'instructions': 'Updated Instructions',  # Ensure all required fields are provided
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, 'Updated ReactRouterBootstrap')

    def test_delete_recipe(self):
        recipe = Recipe.objects.create(
            title='Test ReactRouterBootstrap',
            description='Test Description',
            instructions='Test Instructions',  # Ensure all required fields are provided
            author=self.user
        )
        url = reverse('recipe-detail', kwargs={'pk': recipe.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Recipe.objects.count(), 0)
