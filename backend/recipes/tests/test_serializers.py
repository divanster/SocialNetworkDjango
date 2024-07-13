from django.test import TestCase
from rest_framework.test import APIRequestFactory
from recipes.models import Recipe, Tag, Ingredient, Rating, User
from comments.models import Comment
from recipes.serializers import RecipeSerializer, TagSerializer, IngredientSerializer, RatingSerializer, \
    CommentSerializer


class TagSerializerTests(TestCase):
    def test_tag_serializer(self):
        """Test tag serializer"""
        tag = Tag.objects.create(name='Vegan')
        serializer = TagSerializer(tag)
        self.assertEqual(serializer.data, {'id': tag.id, 'name': 'Vegan'})


class IngredientSerializerTests(TestCase):
    def test_ingredient_serializer(self):
        """Test ingredient serializer"""
        ingredient = Ingredient.objects.create(name='Tomato')
        serializer = IngredientSerializer(ingredient)
        self.assertEqual(serializer.data, {'id': ingredient.id, 'name': 'Tomato'})


class RecipeSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        self.factory = APIRequestFactory()

    def test_create_recipe(self):
        """Test creating a recipe"""
        tag1 = Tag.objects.create(name='Vegan')
        tag2 = Tag.objects.create(name='Dessert')
        ingredient1 = Ingredient.objects.create(name='Tomato')
        ingredient2 = Ingredient.objects.create(name='Basil')
        data = {
            'title': 'Tomato Soup',
            'description': 'A delicious tomato soup recipe.',
            'instructions': 'Boil tomatoes, blend, and serve.',
            'tags': [{'name': 'Vegan'}, {'name': 'Dessert'}],
            'ingredients': [{'name': 'Tomato'}, {'name': 'Basil'}],
        }
        request = self.factory.post('/api/recipes/', data, format='json')
        request.user = self.user
        serializer = RecipeSerializer(data=data, context={'request': request})
        self.assertTrue(serializer.is_valid())
        recipe = serializer.save(author=self.user)
        self.assertEqual(recipe.title, 'Tomato Soup')
        self.assertEqual(recipe.description, 'A delicious tomato soup recipe.')
        self.assertEqual(recipe.instructions, 'Boil tomatoes, blend, and serve.')
        self.assertEqual(recipe.author, self.user)
        self.assertEqual(recipe.tags.count(), 2)
        self.assertEqual(recipe.ingredients.count(), 2)


class RatingSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        self.recipe = Recipe.objects.create(
            title='Test Recipe',
            description='Test Description',
            instructions='Test Instructions',
            author=self.user
        )

    def test_create_rating(self):
        """Test creating a rating"""
        data = {'value': 5}
        serializer = RatingSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        rating = serializer.save(user=self.user, recipe=self.recipe)
        self.assertEqual(rating.value, 5)
        self.assertEqual(rating.user, self.user)
        self.assertEqual(rating.recipe, self.recipe)

    def test_invalid_rating(self):
        """Test creating a rating with invalid data"""
        data = {'value': 6}  # Assuming the max value is 5
        serializer = RatingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('value', serializer.errors)
