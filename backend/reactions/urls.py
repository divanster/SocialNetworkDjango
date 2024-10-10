# backend/reactions/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReactionViewSet

app_name = 'reactions'

router = DefaultRouter()
router.register(r'', ReactionViewSet, basename='reaction')

urlpatterns = [
    path('', include(router.urls)),
]
