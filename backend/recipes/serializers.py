from rest_framework import serializers
from recipes.models import Recipe, Tag, Ingredient, Rating
from comments.models import Comment  # Import Comment from the comments app

class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']

class RatingSerializer(serializers.ModelSerializer):
    value = serializers.IntegerField(min_value=1, max_value=5)
    class Meta:
        model = Rating
        fields = ['id', 'user', 'recipe', 'value']
        read_only_fields = ['id', 'user', 'recipe']

class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments."""

    class Meta:
        model = Comment
        fields = ['id', 'user', 'recipe', 'content', 'created_at']
        read_only_fields = ['id', 'user', 'recipe', 'created_at']

class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2, read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'instructions', 'tags',
            'ingredients', 'average_rating', 'image', 'user'
        ]
        read_only_fields = ['id', 'average_rating']

    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        tag_objects = []
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(name=tag['name'])
            tag_objects.append(tag_obj)
        recipe.tags.set(tag_objects)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""
        ingredient_objects = []
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(name=ingredient['name'])
            ingredient_objects.append(ingredient_obj)
        recipe.ingredients.set(ingredient_objects)

    def create(self, validated_data):
        """Create a recipe."""
        tags = validated_data.pop('tags', [])
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)
        recipe.user = self.context['request'].user
        recipe.save()
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        if tags is not None:
            self._get_or_create_tags(tags, instance)
        if ingredients is not None:
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""
    ratings = RatingSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['ratings', 'comments']

class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}
