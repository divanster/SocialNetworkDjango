from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, RatingViewSet, TagViewSet, IngredientViewSet, RecipeImageViewSet

router = DefaultRouter()
router.register(r'social', RecipeViewSet)
router.register(r'ratings', RatingViewSet)
router.register(r'tags', TagViewSet)
router.register(r'ingredients', IngredientViewSet)
router.register(r'images', RecipeImageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
