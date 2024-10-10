# backend/follows/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FollowViewSet

app_name = 'follows'

router = DefaultRouter()
router.register(r'', FollowViewSet, basename='follow')

urlpatterns = [
    path('', include(router.urls)),
]
