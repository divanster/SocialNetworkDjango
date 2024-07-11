from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import Recipe, Rating, Tag, Ingredient, RecipeImage


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name']


class RecipeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeImage
        fields = ['id', 'image']


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    ingredients = IngredientSerializer(many=True, read_only=True)
    images = RecipeImageSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'description', 'image', 'tags', 'ingredients', 'images',
            'average_rating', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    @extend_schema_field(serializers.FloatField)
    def get_average_rating(self, obj):
        return obj.average_rating


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'recipe', 'user', 'value']
        read_only_fields = ['user']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)
