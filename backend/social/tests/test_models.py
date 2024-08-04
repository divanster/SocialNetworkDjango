from django.test import TestCase
from django.contrib.auth import get_user_model
from social.models import Recipe, Tag, Ingredient, Rating

User = get_user_model()


class RecipeModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
        self.tag = Tag.objects.create(name='Vegan')
        self.ingredient = Ingredient.objects.create(name='Tomato')

    def test_create_recipe(self):
        recipe = Recipe.objects.create(
            title='Test ReactRouterBootstrap',
            description='Test Description',
            author=self.user
        )
        recipe.tags.add(self.tag)
        recipe.ingredients.add(self.ingredient)

        self.assertEqual(recipe.title, 'Test ReactRouterBootstrap')
        self.assertEqual(recipe.description, 'Test Description')
        self.assertEqual(recipe.author, self.user)
        self.assertIn(self.tag, recipe.tags.all())
        self.assertIn(self.ingredient, recipe.ingredients.all())

    def test_recipe_str(self):
        recipe = Recipe.objects.create(
            title='Test ReactRouterBootstrap',
            description='Test Description',
            author=self.user
        )
        self.assertEqual(str(recipe), 'Test ReactRouterBootstrap')

    def test_average_rating(self):
        recipe = Recipe.objects.create(
            title='Test ReactRouterBootstrap',
            description='Test Description',
            author=self.user
        )
        Rating.objects.create(recipe=recipe, user=self.user, value=4)
        Rating.objects.create(recipe=recipe, user=self.user2, value=2)

        self.assertEqual(recipe.average_rating, 3)
