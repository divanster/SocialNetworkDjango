# backend/pages/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PageViewSet

app_name = 'pages'

router = DefaultRouter()
router.register(r'', PageViewSet, basename='page')

urlpatterns = [
    path('', include(router.urls)),
]
