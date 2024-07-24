# backend/reactions/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReactionViewSet

router = DefaultRouter()
router.register(r'reactions', ReactionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
